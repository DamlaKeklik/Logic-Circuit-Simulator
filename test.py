import unittest
import tkinter as tk
from main import Application, InputGate, OrGate, Lamp


class TestApplicationMethods(unittest.TestCase):
    def setUp(self):
        # Uygulama örneğini oluştur
        self.root = tk.Tk()
        self.app = Application(self.root)

    def test_or_gate_with_two_inputs_and_led(self):
        # İki giriş kapısı ve bir OR kapısı ekleyin
        self.app.add_input_gate()
        self.app.add_input_gate()
        self.app.add_or_gate()

        # İlk giriş kapısını "1" olarak ayarlayın
        input_gate1 = self.app.gates[0]
        input_gate1.toggle_state()

        # İkinci giriş kapısını "0" olarak ayarlayın
        input_gate2 = self.app.gates[1]

        # OR kapısını seçin
        or_gate = self.app.gates[2]

        # İki giriş kapısını OR kapısına bağlayın
        or_gate.add_input(input_gate1)
        or_gate.add_input(input_gate2)

        # LED ekleyin
        self.app.add_lamp()
        lamp = self.app.lamps[0]

        # OR kapısını LED'e bağlayın
        lamp.add_input(or_gate)

        # Simülasyonu başlatın
        self.app.run_simulation()

        # Simülasyonu değerlendirin
        self.app.evaluate()

        # LED'in durumunu kontrol edin
        self.assertTrue(lamp.state, "LED should be ON when any input to OR gate is ON")


if __name__ == '__main__':
    unittest.main()
