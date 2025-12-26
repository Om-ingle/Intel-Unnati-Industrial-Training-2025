from main import TranslationService
import time

def main():
    translator = TranslationService()

    hi_text = "जीवन एक चॉकलेट बॉक्स की तरह है।"
    chinese_text = "生活就像一盒巧克力。"
    start = time.time()
        
    translated_hi_text = translator.translate(hi_text, "hi", "fr")
    print(f"Hindi to French: {translated_hi_text}")
    total = time.time() - start
    print("Total Time taken: ", total)

    start = time.time()
    translated_zh_text = translator.translate(chinese_text, "zh", "en")
    print(f"Chinese to English: {translated_zh_text}")
    total = time.time() - start
    print("Total Time Taken: ", total)
    print(total)

if __name__ == "__main__":
    main()
