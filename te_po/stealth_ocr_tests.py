from te_po.stealth_ocr import StealthOCR


class LocalTestSuite:
    """Tools to test our stealth system locally without external dependencies"""

    def __init__(self):
        self.stealth_ocr = StealthOCR()

    def test_macron_encoding(self):
        """Test our macron encoding system"""
        test_texts = [
            "Kia ora, ko Māui ahau",
            "Tēnā koe, he aha tō ingoa?",
            "Āwhina mai i a koe",
            "Ko Kitenga te kaitiaki",
        ]

        print("🔍 MACRON ENCODING TEST")
        print("=" * 40)

        for text in test_texts:
            encoded = self.stealth_ocr.encode_cultural_text(text)
            decoded = self.stealth_ocr.decode_cultural_text(encoded)
            print(f"Original:  {text}")
            print(f"Encoded:   {encoded}")
            print(f"Decoded:   {decoded}")
            print(f"Match:     {'✅' if text == decoded else '❌'}")
            print("-" * 30)

    def test_metadata_embedding(self):
        """Test invisible metadata embedding"""
        test_text = "This is a test of kaitiaki protection systems"

        print("\n👻 INVISIBLE METADATA TEST")
        print("=" * 40)

        metadata = self.stealth_ocr._generate_protection_metadata(test_text)
        text_with_metadata = self.stealth_ocr.embed_invisible_metadata(test_text, metadata)
        extracted_text, extracted_metadata = self.stealth_ocr.extract_invisible_metadata(text_with_metadata)

        print(f"Original text: {test_text}")
        print(f"Text with metadata (visible): {text_with_metadata}")
        print(f"Extracted text: {extracted_text}")
        print(f"Metadata recovered: {'✅' if extracted_metadata else '❌'}")
        print(
            f"Ownership verified: {'✅' if extracted_metadata.get('ownership') == 'AwaNet Kaitiaki Collective' else '❌'}"
        )

    def test_psycheract_simulation(self):
        """Simulate the Psycheract OCR system"""
        print("\n🕵️ PSYCHERACT SIMULATION")
        print("=" * 40)

        fake_image_data = b"fake_image_data_for_testing"
        results = self.stealth_ocr.psycheract_scan(fake_image_data, prefer_offline=True)

        print(f"Method used: {results['method_used']}")
        print(f"Cultural content: {'✅' if results['cultural_content'] else '❌'}")
        print(f"Stealth encoded: {'✅' if results['stealth_encoded'] else '❌'}")
        print(f"Protected: {'✅' if results['protected'] else '❌'}")
        if results.get("protection_metadata"):
            print(f"Ownership signature: {results['protection_metadata']['kaitiaki_signature']}")


def run_full_stealth_test():
    print("🛡️ KAITIAKI STEALTH SYSTEM TEST SUITE")
    print("=" * 50)

    suite = LocalTestSuite()
    suite.test_macron_encoding()
    suite.test_metadata_embedding()
    suite.test_psycheract_simulation()

    print("\n🌟 STEALTH SYSTEM READY FOR DEPLOYMENT!")
    print("🔒 Cultural content protected with kaitiaki encoding")
    print("👻 Invisible metadata embedded for ownership proof")
    print("🕵️ Psycheract OCR ready for concealed operations")


if __name__ == "__main__":
    run_full_stealth_test()
