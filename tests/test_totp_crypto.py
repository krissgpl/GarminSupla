import unittest

from cryptography.fernet import Fernet

from app.security.totp_crypto import TotpSecretCipher


class TotpSecretCipherTests(unittest.TestCase):

    def setUp(self):
        self.key = Fernet.generate_key().decode(
            "ascii"
        )

        self.cipher = TotpSecretCipher(
            self.key
        )

        self.secret = "JBSWY3DPEHPK3PXP"

    def test_encrypt_decrypt_round_trip(self):
        encrypted = self.cipher.encrypt(
            self.secret
        )

        self.assertNotEqual(
            encrypted,
            self.secret,
        )

        self.assertEqual(
            self.cipher.decrypt(encrypted),
            self.secret,
        )

    def test_encryption_is_randomized(self):
        first = self.cipher.encrypt(
            self.secret
        )

        second = self.cipher.encrypt(
            self.secret
        )

        self.assertNotEqual(
            first,
            second,
        )

    def test_wrong_key_is_rejected(self):
        encrypted = self.cipher.encrypt(
            self.secret
        )

        other_cipher = TotpSecretCipher(
            Fernet.generate_key().decode(
                "ascii"
            )
        )

        with self.assertRaises(ValueError):
            other_cipher.decrypt(
                encrypted
            )

    def test_modified_ciphertext_is_rejected(self):
        encrypted = self.cipher.encrypt(
            self.secret
        )

        replacement = (
            "A"
            if encrypted[20] != "A"
            else "B"
        )

        modified = (
            encrypted[:20]
            + replacement
            + encrypted[21:]
        )

        with self.assertRaises(ValueError):
            self.cipher.decrypt(
                modified
            )

    def test_invalid_key_is_rejected(self):
        with self.assertRaises(ValueError):
            TotpSecretCipher(
                "invalid-key"
            )


if __name__ == "__main__":
    unittest.main()
