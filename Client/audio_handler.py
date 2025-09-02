import pyaudio
import logging
import queue
import base64
import threading
import time
import numpy as np
from shared import config

logging.basicConfig(level=logging.INFO)

class AudioHandler:
    def __init__(self, network_handler=None):
        self.audio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self.is_recording = False
        self.is_playing = False
        self.muted = False
        self.network_handler = network_handler
        self.audio_devices = []  # Lưu danh sách thiết bị

        # Audio buffers
        self.audio_queue = queue.Queue(maxsize=10)
        
        # Echo cancellation improved
        self.echo_buffer = queue.Queue(maxsize=3)
        self.echo_threshold = 0.3
        
        # Thread management
        self.record_thread = None
        self.playback_thread = None
        self.running = True
        
        # Thread safety
        self.record_lock = threading.Lock()
        self.playback_lock = threading.Lock()
        
        # Audio processing stats
        self.audio_stats = {'sent': 0, 'received': 0, 'dropped': 0}
        
        self._list_audio_devices()

    def _list_audio_devices(self):
        """Liệt kê tất cả thiết bị âm thanh và lưu vào self.audio_devices."""
        try:
            info = self.audio.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            self.audio_devices = []
            for i in range(num_devices):
                device = self.audio.get_device_info_by_host_api_device_index(0, i)
                device_info = {
                    'index': i,
                    'name': device['name'],
                    'input_channels': device['maxInputChannels'],
                    'output_channels': device['maxOutputChannels']
                }
                self.audio_devices.append(device_info)
                logging.info(f"Device {i}: {device['name']}, Input Channels: {device['maxInputChannels']}, Output Channels: {device['maxOutputChannels']}")
            return self.audio_devices
        except Exception as e:
            logging.error(f"[AudioHandler] Error listing audio devices: {e}")
            return []

    def get_audio_devices(self):
        """Trả về danh sách thiết bị âm thanh."""
        return self.audio_devices

    def _process_audio_chunk(self, data, is_input=True):
        """Xử lý audio chunk với echo cancellation cải tiến"""
        if len(data) == 0:
            return None
            
        try:
            # Convert to numpy array for processing
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            
            # Normalize audio
            audio_data = audio_data / 32768.0
            
            if is_input:
                # Input processing - noise gate và echo cancellation
                if np.max(np.abs(audio_data)) < config.SILENCE_THRESHOLD / 32768.0:
                    return None
                    
                # Echo cancellation - so sánh với output gần đây
                if not self.echo_buffer.empty():
                    try:
                        echo_data = self.echo_buffer.get_nowait()
                        # Tính correlation chỉ nếu kích thước phù hợp
                        min_len = min(len(audio_data), len(echo_data))
                        if min_len > 10:  # Đảm bảo có đủ dữ liệu để so sánh
                            echo_similarity = np.correlate(
                                audio_data[:min_len], 
                                echo_data[:min_len]
                            )[0] / (np.linalg.norm(audio_data[:min_len]) * np.linalg.norm(echo_data[:min_len]) + 1e-10)
                            
                            if echo_similarity > self.echo_threshold:
                                logging.debug(f"[AudioHandler] Echo detected: {echo_similarity:.2f}")
                                return None
                    except (queue.Empty, ValueError):
                        pass
                        
                return (audio_data * 32768.0).astype(np.int16).tobytes()
            else:
                # Output processing - lưu vào echo buffer
                if not self.echo_buffer.full():
                    self.echo_buffer.put(audio_data.copy())
                return data
                
        except Exception as e:
            logging.error(f"[AudioHandler] Audio processing error: {e}")
            return None

    def start_recording(self, send_callback=None, input_device_index=None):
        """Bắt đầu ghi âm với echo cancellation cải tiến"""
        with self.record_lock:
            if self.is_recording:
                return
                
            self.is_recording = True
            
        self.record_thread = threading.Thread(
            target=self._record_loop,
            args=(send_callback, input_device_index),
            daemon=True
        )
        self.record_thread.start()

    def _record_loop(self, send_callback, input_device_index):
        """Vòng lặp ghi âm với echo cancellation cải tiến"""
        try:
            self.input_stream = self.audio.open(
                format=config.AUDIO_FORMAT,
                channels=config.AUDIO_CHANNELS,
                rate=config.AUDIO_RATE,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=config.AUDIO_CHUNK
            )
            
            logging.info(f"[AudioHandler] Started recording at {config.AUDIO_RATE}Hz, chunk: {config.AUDIO_CHUNK}")
            
            while self.is_recording and self.running:
                try:
                    # Đọc dữ liệu audio
                    data = self.input_stream.read(config.AUDIO_CHUNK, exception_on_overflow=False)
                    
                    if not data or len(data) == 0:
                        time.sleep(0.01)
                        continue
                    
                    # Xử lý echo cancellation
                    processed_data = self._process_audio_chunk(data, is_input=True)
                    if processed_data and not self.muted:
                        if send_callback:
                            send_callback(processed_data)
                        elif (self.network_handler and 
                              hasattr(self.network_handler, 'is_connected') and 
                              self.network_handler.is_connected()):
                            try:
                                audio_b64 = base64.b64encode(processed_data).decode('utf-8')
                                success = self.network_handler.send_message({
                                    'type': 'AUDIO_DATA',
                                    'data': audio_b64
                                })
                                if success:
                                    self.audio_stats['sent'] += 1
                                else:
                                    self.audio_stats['dropped'] += 1
                            except Exception as e:
                                logging.error(f"[AudioHandler] Network send error: {e}")
                                self.audio_stats['dropped'] += 1
                            
                except Exception as e:
                    if self.is_recording:  # Chỉ log nếu vẫn đang recording
                        logging.error(f"[AudioHandler] Recording loop error: {e}")
                    break
                    
        except Exception as e:
            logging.error(f"[AudioHandler] Recording setup error: {e}")
        finally:
            self.stop_recording()

    def start_playback(self, get_callback=None, output_device_index=None):
        """Bắt đầu phát audio"""
        with self.playback_lock:
            if self.is_playing:
                return
                
            self.is_playing = True
            
        self.playback_thread = threading.Thread(
            target=self._playback_loop,
            args=(get_callback, output_device_index),
            daemon=True
        )
        self.playback_thread.start()

    def _playback_loop(self, get_callback, output_device_index):
        """Vòng lặp phát audio với echo cancellation"""
        try:
            sample_size = self.audio.get_sample_size(config.AUDIO_FORMAT)
            bytes_per_chunk = config.AUDIO_CHUNK * sample_size * config.AUDIO_CHANNELS

            self.output_stream = self.audio.open(
                format=config.AUDIO_FORMAT,
                channels=config.AUDIO_CHANNELS,
                rate=config.AUDIO_RATE,
                output=True,
                output_device_index=output_device_index,
                frames_per_buffer=config.AUDIO_CHUNK
            )
            
            logging.info(f"[AudioHandler] Started playback at {config.AUDIO_RATE}Hz")
            
            while self.is_playing and self.running:
                try:
                    # Lấy dữ liệu audio để phát
                    if get_callback:
                        data = get_callback()
                    elif not self.audio_queue.empty():
                        data = self.audio_queue.get_nowait()
                    else:
                        # Silence nếu không có data
                        data = b'\x00' * bytes_per_chunk
                        time.sleep(0.01)
                        continue
                    
                    # Xử lý output và lưu vào echo buffer
                    if data:
                        processed_data = self._process_audio_chunk(data, is_input=False)
                        if processed_data:
                            self.output_stream.write(processed_data)
                    
                except queue.Empty:
                    # Queue rỗng, phát silence
                    silence = b'\x00' * bytes_per_chunk
                    self.output_stream.write(silence)
                    time.sleep(0.01)
                except Exception as e:
                    if self.is_playing:  # Chỉ log nếu vẫn đang playing
                        logging.error(f"[AudioHandler] Playback loop error: {e}")
                    break
                    
        except Exception as e:
            logging.error(f"[AudioHandler] Playback setup error: {e}")
        finally:
            self.stop_playback()

    def stop_recording(self):
        """Dừng ghi âm một cách an toàn"""
        with self.record_lock:
            if not self.is_recording:
                return
                
            self.is_recording = False
            
        if self.input_stream:
            try:
                # Dừng stream trước khi đóng
                if self.input_stream.is_active():
                    self.input_stream.stop_stream()
                self.input_stream.close()
            except Exception as e:
                logging.error(f"[AudioHandler] Error stopping input stream: {e}")
            finally:
                self.input_stream = None
                
        # Đợi thread kết thúc
        if self.record_thread and self.record_thread.is_alive():
            try:
                self.record_thread.join(timeout=1.0)
            except Exception:
                pass
                
        logging.info("[AudioHandler] Stopped recording")

    def stop_playback(self):
        """Dừng phát audio một cách an toàn"""
        with self.playback_lock:
            if not self.is_playing:
                return
                
            self.is_playing = False
            
        if self.output_stream:
            try:
                # Dừng stream trước khi đóng
                if self.output_stream.is_active():
                    self.output_stream.stop_stream()
                self.output_stream.close()
            except Exception as e:
                logging.error(f"[AudioHandler] Error stopping output stream: {e}")
            finally:
                self.output_stream = None
        
        # Xóa queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        # Đợi thread kết thúc
        if self.playback_thread and self.playback_thread.is_alive():
            try:
                self.playback_thread.join(timeout=1.0)
            except Exception:
                pass
                
        logging.info("[AudioHandler] Stopped playback")

    def toggle_mute(self):
        """Chuyển đổi trạng thái mute"""
        self.muted = not self.muted
        return self.muted

    def get_audio_stats(self):
        """Lấy thống kê audio"""
        return self.audio_stats.copy()

    def cleanup(self):
        """Dọn dẹp tài nguyên một cách an toàn"""
        self.running = False
        
        # Dừng recording và playback
        self.stop_recording()
        self.stop_playback()
        
        # Giải phóng PyAudio
        try:
            self.audio.terminate()
        except Exception as e:
            logging.error(f"[AudioHandler] Error terminating audio: {e}")
        
        # Xóa buffer echo
        while not self.echo_buffer.empty():
            try:
                self.echo_buffer.get_nowait()
            except queue.Empty:
                break
                
        logging.info("[AudioHandler] Cleanup completed")

    def handle_audio_data(self, message):
        """Nhận chuỗi base64 từ network và đưa vào queue phát"""
        try:
            if 'data' not in message:
                logging.warning("[AudioHandler] Message missing 'data' field")
                return
                
            audio_data = base64.b64decode(message['data'])
            if len(audio_data) == 0:
                logging.debug("[AudioHandler] Empty audio data received")
                return
                
            # Kiểm tra nếu queue đầy thì bỏ qua
            if self.audio_queue.full():
                self.audio_stats['dropped'] += 1
                return
                
            self.audio_queue.put(audio_data)
            self.audio_stats['received'] += 1
            
        except Exception as e:
            logging.error(f"[AudioHandler] Audio data processing error: {e}")