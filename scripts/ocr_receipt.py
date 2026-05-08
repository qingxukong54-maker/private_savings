import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

from openocr import OpenOCR

ocr = OpenOCR(task='ocr', mode='mobile', backend='onnx')

image_path = sys.argv[1] if len(sys.argv) > 1 else r'E:\finance_vault\raw\receipts\processed\c9dd0969dd3251a8e43a6d844e985dfb.jpg'
results, time_dicts = ocr(image_path=image_path)

print("=== OCR Results ===")
for result in results:
    if isinstance(result, dict) and 'transcription' in result:
        score = result.get('score', 0)
        text = result['transcription']
        if score > 0.7:
            print(f"{text}  (score: {score:.3f})")
    elif isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and 'transcription' in item:
                score = item.get('score', 0)
                text = item['transcription']
                if score > 0.7:
                    print(f"{text}  (score: {score:.3f})")
