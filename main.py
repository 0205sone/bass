import pygame
import sounddevice as sd
import numpy as np
import librosa

# 音階の基本周波数
TARGET_FREQUENCIES = {
    "E": 41.2,
    "A": 55.0,
    "D": 73.4,
    "G": 98.0
}

# Pygameの初期化
pygame.init()

# ウィンドウの設定
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bass Tuner")

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# フォント設定
font = pygame.font.Font(None, 36)

# 音階選択ボタンの座標
buttons = {
    "E": pygame.Rect(100, 300, 100, 50),
    "A": pygame.Rect(250, 300, 100, 50),
    "D": pygame.Rect(400, 300, 100, 50),
    "G": pygame.Rect(550, 300, 100, 50),
}

# 現在のターゲット音階
current_target = "E"

# マイク設定
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024


def get_pitch(data, sample_rate):
  """音高を取得する"""
  data = data / np.max(np.abs(data))  # 正規化
  pitches = librosa.pyin(data, fmin=30, fmax=500, sr=sample_rate)
  if pitches is not None and len(pitches) > 0:
    return np.nanmean(pitches)  # NaNを除外して平均値を返す
  return 0


def audio_callback(indata, frames, time, status):
  global detected_pitch
  mono_data = np.mean(indata, axis=1)
  detected_pitch = get_pitch(mono_data.astype(np.float32), SAMPLE_RATE)


# 音高検出の初期値
sd.InputStream(callback=audio_callback, channels=1,
               samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE).start()
detected_pitch = 0

# メインループ
running = True
while running:
  screen.fill(WHITE)

  # イベント処理
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      for note, rect in buttons.items():
        if rect.collidepoint(event.pos):
          current_target = note

  # 音階差の計算
  target_freq = TARGET_FREQUENCIES[current_target]
  diff = detected_pitch - target_freq

  # テキスト描画
  pitch_text = font.render(
      f"Detected Pitch: {detected_pitch:.2f} Hz", True, BLACK)
  target_text = font.render(
      f"Target: {current_target} ({target_freq:.2f} Hz)", True, BLACK)
  diff_text = font.render(
      f"Difference: {diff:+.2f} Hz", True, GREEN if abs(diff) < 1 else RED)

  screen.blit(pitch_text, (50, 50))
  screen.blit(target_text, (50, 100))
  screen.blit(diff_text, (50, 150))

  # ボタン描画
  for note, rect in buttons.items():
    color = GREEN if note == current_target else BLACK
    pygame.draw.rect(screen, color, rect, 2)
    button_text = font.render(note, True, BLACK)
    screen.blit(button_text, (rect.x + 25, rect.y + 10))

  pygame.display.flip()

pygame.quit()
