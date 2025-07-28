import tkinter as tk
from tkinter import messagebox

class Connection:
    def __init__(self, canvas, start_gate, end_gate):
        self.canvas = canvas
        self.start_gate = start_gate
        self.end_gate = end_gate
        self.line = self.canvas.create_line(self.get_coords(), fill="blue")

    def get_coords(self):
        start_coords = self.canvas.coords(self.start_gate.connection_point)
        end_coords = self.canvas.coords(self.end_gate.connection_point)
        return (start_coords[0] + 5, start_coords[1] + 5, end_coords[0] + 5, end_coords[1] + 5)

    def update_position(self):
        color = "green" if self.start_gate.output else "blue"
        self.canvas.coords(self.line, self.get_coords())
        self.canvas.itemconfig(self.line, fill=color)

class Gate:
    def __init__(self, canvas, x, y, label):
        self.inputs = []
        self.output = False
        self.label = label
        self.canvas = canvas
        self.text = self.canvas.create_text(x, y, text=label, anchor="w")
        self.x = x
        self.y = y
        self.connection_point = self.canvas.create_oval(x + 30, y - 5, x + 40, y + 5, fill="black")
        self.connections = []
        self.canvas.tag_bind(self.text, "<ButtonPress-1>", self.handle_press)
        self.canvas.tag_bind(self.text, "<B1-Motion>", self.handle_motion)
        self.canvas.tag_bind(self.text, "<ButtonRelease-1>", self.handle_release)

    def add_input(self, input_gate):
        self.inputs.append(input_gate)
        connection = Connection(self.canvas, input_gate, self)
        self.connections.append(connection)
        input_gate.connections.append(connection)

    def evaluate(self):
        self.update_connections()

    def update_connections(self):
        for connection in self.connections:
            connection.update_position()

    def move(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y
        self.canvas.move(self.text, delta_x, delta_y)
        self.canvas.move(self.connection_point, delta_x, delta_y)
        for connection in self.connections:
            connection.update_position()

    def handle_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def handle_motion(self, event):
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        self.move(delta_x, delta_y)
        self.start_x = event.x
        self.start_y = event.y

    def handle_release(self, event):
        pass

class OutputGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "Çıkış")
        self.input = None

    def set_input(self, value, input_gate=None):
        self.input = input_gate

    def evaluate(self):
        if self.input is None:
            return False
        return self.input.output

    def move(self, delta_x, delta_y):
        super().move(delta_x, delta_y)

    def add_input(self, input_gate):
        self.inputs.append(input_gate)
        connection = Connection(self.canvas, input_gate, self)
        self.connections.append(connection)
        input_gate.connections.append(connection)

    def is_connected_to_output_gate(self):
        for input_gate in self.inputs:
            if isinstance(input_gate, OutputGate):
                return True
        return False

    def update_state(self):
        if self.inputs:
            self.state = any(input_gate.output for input_gate in self.inputs)
        else:
            self.state = False
        self.update_text()
        if self.state:
            self.canvas.itemconfig(self.body, fill="green")
        else:
            self.canvas.itemconfig(self.body, fill="red")

    def toggle_state(self):
        self.state = not self.state
        self.update_text()

    def update_text(self):
        if self.state:
            self.canvas.itemconfig(self.text, text="1", fill="green")
        else:
            self.canvas.itemconfig(self.text, text="0", fill="red")

    def evaluate(self):
        if len(self.inputs) > 0 and isinstance(self.inputs[0], OutputGate):
            self.state = self.inputs[0].evaluate()
        else:
            if self.inputs:
                self.state = any(input_gate.output for input_gate in self.inputs)
            else:
                self.state = False
        self.update_text()
        self.update_connections()

class NandGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "NAND")

    def evaluate(self):
        if self.inputs:
            self.output = not all(input_gate.output for input_gate in self.inputs)
        else:
            self.output = False
        super().evaluate()

class NorGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "NOR")

    def evaluate(self):
        if self.inputs:
            self.output = not any(input_gate.output for input_gate in self.inputs)
        else:
            self.output = False
        super().evaluate()

class XorGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "XOR")

    def evaluate(self):
        if len(self.inputs) == 2:
            input1, input2 = self.inputs
            self.output = input1.output != input2.output
        else:
            self.output = False
        super().evaluate()

class AndGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "AND")

    def evaluate(self):
        if self.inputs:
            self.output = all(input_gate.output for input_gate in self.inputs)
        else:
            self.output = False
        super().evaluate()

class XnorGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "XNOR")

    def evaluate(self):
        if self.inputs:
            input_values = [input_gate.output for input_gate in self.inputs]
            if all(input_values) or not any(input_values):
                self.output = True
            else:
                self.output = False
        else:
            self.output = False
        super().evaluate()

class NotGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "NOT")

    def evaluate(self):
        if len(self.inputs) > 1:
            messagebox.showerror("Hata", "Not kapısı için birden fazla giriş bulunmaktadır.")
            self.canvas.master.quit()
            return
        if self.inputs:
            input_gate = self.inputs[0]
            self.output = not input_gate.output
        else:
            self.output = False
        super().evaluate()

class BufferGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "Buffer")

    def add_input(self, input_gate):
        if len(self.inputs) < 1:
            super().add_input(input_gate)
        else:
            messagebox.showerror("Hata", "Buffer kapısının yalnızca bir girişi olabilir!")
            self.canvas.master.quit()

    def evaluate(self):
        if self.inputs:
            self.output = self.inputs[0].output
        else:
            self.output = False
        super().evaluate()

class OrGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "OR")

    def evaluate(self):
        if self.inputs:
            self.output = any(input_gate.output for input_gate in self.inputs)
        else:
            self.output = False
        super().evaluate()

class InputGate(Gate):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, "Giriş")
        self.state = False
        self.output = self.state
        self.button = tk.Button(canvas.master, text="0", command=self.toggle_state)
        self.button_window = self.canvas.create_window(x + 53, y, window=self.button)
        self.canvas.tag_bind(self.button_window, "<ButtonPress-1>", self.handle_press)
        self.canvas.tag_bind(self.button_window, "<B1-Motion>", self.handle_motion)
        self.canvas.tag_bind(self.button_window, "<ButtonRelease-1>", self.handle_release)

    def toggle_state(self):
        self.state = not self.state
        self.output = self.state
        self.button.config(text="1" if self.state else "0")
        for connection in self.connections:
            connection.update_position()

    def move(self, delta_x, delta_y):
        super().move(delta_x, delta_y)
        self.canvas.move(self.button_window, delta_x, delta_y)

    def handle_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def handle_motion(self, event):
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        self.move(delta_x, delta_y)
        self.start_x = event.x
        self.start_y = event.y

    def handle_release(self, event):
        pass

    def evaluate(self):
        self.output = self.state

class Lamp:
    def __init__(self, canvas, x, y):
        self.inputs = []
        self.state = False
        self.x = x
        self.y = y
        self.canvas = canvas
        self.body = self.canvas.create_oval(x, y, x + 40, y + 40, fill="red")
        self.text = self.canvas.create_text(x + 20, y + 50, text="Kapalı")
        self.connection_point = self.canvas.create_oval(x - 17, y + 15, x - 3, y + 30, fill="black")
        self.connections = []
        self.canvas.tag_bind(self.body, "<ButtonPress-1>", self.handle_press)
        self.canvas.tag_bind(self.body, "<B1-Motion>", self.handle_motion)
        self.canvas.tag_bind(self.body, "<ButtonRelease-1>", self.handle_release)
        self.output = False

    def add_input(self, input_gate):
        self.inputs.append(input_gate)
        connection = Connection(self.canvas, input_gate, self)
        self.connections.append(connection)
        input_gate.connections.append(connection)

    def is_connected_to_output_gate(self):
        for input_gate in self.inputs:
            if isinstance(input_gate, OutputGate):
                return True
        return False

    def update_state(self):
        if self.inputs:
            self.state = any(input_gate.output for input_gate in self.inputs)
        else:
            self.state = False
        if self.state:
            self.canvas.itemconfig(self.body, fill="green")
            self.canvas.itemconfig(self.text, text="Açık")
        else:
            self.canvas.itemconfig(self.body, fill="red")
            self.canvas.itemconfig(self.text, text="Kapalı")

    def move(self, delta_x, delta_y):
        self.x += delta_x  # X koordinatını güncelle
        self.y += delta_y  # Y koordinatını güncelle
        self.canvas.move(self.body, delta_x, delta_y)
        self.canvas.move(self.text, delta_x, delta_y)
        self.canvas.move(self.connection_point, delta_x, delta_y)
        for connection in self.connections:
            connection.update_position()

    def handle_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def handle_motion(self, event):
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        self.move(delta_x, delta_y)
        self.start_x = event.x
        self.start_y = event.y

    def handle_release(self, event):
        pass

    def toggle_state(self):
        self.state = not self.state
        self.update_state()

    def evaluate(self):
        if len(self.inputs) > 0 and isinstance(self.inputs[0], OutputGate):
            self.state = self.inputs[0].evaluate()
        else:
            if self.inputs:
                self.state = any(input_gate.output for input_gate in self.inputs)
            else:
                self.state = False
        if self.state:
            self.canvas.itemconfig(self.body, fill="green")
            self.canvas.itemconfig(self.text, text="Açık")
        else:
            self.canvas.itemconfig(self.body, fill="red")
            self.canvas.itemconfig(self.text, text="Kapalı")

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Sayısal Tasarım Simülasyonu")
        self.root.geometry("800x600")
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.gates = []
        self.lamps = []
        self.is_connecting = False
        self.selected_gate = None
        self.selected_connection_start = None
        self.connection_line = None
        self.output_gate = None
        self.simulation_running = None
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        element_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Mantık Kapıları", menu=element_menu)
        element_menu.add_command(label="AND", command=self.add_and_gate)
        element_menu.add_command(label="OR", command=self.add_or_gate)
        element_menu.add_command(label="NOT", command=self.add_not_gate)
        element_menu.add_command(label="Buffer", command=self.add_buffer_gate)
        element_menu.add_command(label="NAND", command=self.add_nand_gate)
        element_menu.add_command(label="NOR", command=self.add_nor_gate)
        element_menu.add_command(label="XOR", command=self.add_xor_gate)
        element_menu.add_command(label="XNOR", command=self.add_xnor_gate)
        io_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Giriş Çıkış Elemanları", menu=io_menu)
        io_menu.add_command(label="Giriş", command=self.add_input_gate)
        io_menu.add_command(label="Çıkış", command=self.add_output_gate)
        io_menu.add_command(label="LED", command=self.add_lamp)
        connection_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Bağlantı Elemanları", menu=connection_menu)
        connection_menu.add_command(label="Bağlantı Düğümü", command=self.start_connection)
        control_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Kontrol Tuşları", menu=control_menu)
        control_menu.add_command(label="Çalıştır", command=self.run_simulation)
        control_menu.add_command(label="Reset", command=self.reset_simulation)
        control_menu.add_command(label="Durdur", command=self.stop_simulation)
        self.canvas.bind("<ButtonPress-1>", self.handle_press)
        self.canvas.bind("<B1-Motion>", self.handle_motion)
        self.canvas.bind("<ButtonRelease-1>", self.handle_release)

    def add_input_gate(self):
        input_gate = InputGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(input_gate)

    def add_not_gate(self):
        not_gate = NotGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(not_gate)

    def add_output_gate(self):
        output_gate = OutputGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(output_gate)

    def add_buffer_gate(self):
        buffer_gate = BufferGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(buffer_gate)

    def add_and_gate(self):
        and_gate = AndGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(and_gate)

    def add_or_gate(self):
        or_gate = OrGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(or_gate)

    def add_nand_gate(self):
        nand_gate = NandGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(nand_gate)

    def add_nor_gate(self):
        nor_gate = NorGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(nor_gate)

    def add_xor_gate(self):
        xor_gate = XorGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(xor_gate)

    def add_xnor_gate(self):
        xnor_gate = XnorGate(self.canvas, 50, 50 + len(self.gates) * 50)
        self.gates.append(xnor_gate)

    def add_lamp(self):
        lamp = Lamp(self.canvas, 300, 50 + len(self.lamps) * 50)
        self.lamps.append(lamp)

    def start_connection(self):
        self.is_connecting = True

    # Tıklamanın herhangi bir kapının veya lambanın bağlantı alanı içinde olup olmadığını kontrol eder
    def handle_press(self, event):
        if self.is_connecting:
            for gate in self.gates:
                x, y, _, _ = self.canvas.coords(gate.connection_point)
                if x < event.x < x + 10 and y < event.y < y + 10:
                    self.selected_gate = gate
                    self.selected_connection_start = (x + 5, y + 5)
                    return
            for lamp in self.lamps:
                x, y, _, _ = self.canvas.coords(lamp.connection_point)
                if x < event.x < x + 10 and y < event.y < y + 10:
                    self.selected_gate = lamp
                    self.selected_connection_start = (x + 5, y + 5)
                    return

    # Kullanıcı fareyi sürükledikçe tuval üzerindeki bağlantı hattını dinamik olarak günceller
    def handle_motion(self, event):
        if self.is_connecting and self.selected_gate:
            if self.connection_line:
                self.canvas.delete(self.connection_line)
            self.connection_line = self.canvas.create_line(self.selected_connection_start[0],
                                                           self.selected_connection_start[1], event.x, event.y,
                                                           fill="blue")

    def handle_release(self, event):
        if self.selected_gate and self.connection_line:
            for gate in self.gates:
                x, y, x1, y1 = self.canvas.coords(gate.connection_point)
                if gate != self.selected_gate and x < event.x < x1 and y < event.y < y1:
                    gate.add_input(self.selected_gate)
                    self.canvas.delete(self.connection_line)
                    return
            for lamp in self.lamps:
                x, y, x1, y1 = self.canvas.coords(lamp.connection_point)
                if lamp != self.selected_gate and x < event.x < x1 and y < y1:
                    lamp.add_input(self.selected_gate)
                    self.canvas.delete(self.connection_line)
                    return
            self.canvas.delete(self.connection_line)
        self.connection_line = None
        self.selected_gate = None
        self.selected_connection_start = None
        self.is_connecting = False

    def live_evaluation(self):
        if not any(isinstance(gate, InputGate) for gate in self.gates):
            print("Hiçbir giriş kapısı bağlı değil. Sistem değerlendiremiyor.")
            return

        # Doğru değerlendirme sırasını sağlamak için kapıları topolojik olarak sıralayın
        sorted_gates = self.topological_sort(self.gates)

        # Tüm kapıları doğru sırayla değerlendirin
        for gate in sorted_gates:
            gate.evaluate()

        # Lambaları güncelle
        for lamp in self.lamps:
            lamp.update_state()

        # Simülasyonun devam etmesi mi yoksa durması mı gerektiğini kontrol edin
        if self.simulation_running:
            # Bir sonraki canlı değerlendirmeyi planlayın
            self.root.after(50, self.live_evaluation)  # Zaman aralığını ayarlayın (1000 ms = 1 saniye)

    def run_simulation(self):
        self.simulation_running = True
        messagebox.showinfo("Bilgi", "Simülasyon başlatıldı.")
        # Simülasyon başladıktan sonra canlı değerlendirmeyi başlatın
        self.live_evaluation()

    def stop_simulation(self):
        self.simulation_running = False
        messagebox.showinfo("Bilgi", "Simülasyon durduruldu.")

    def evaluate(self):
        if not self.output_gate:
            print("Çıkış kapısı mevcut değil. Sistem değerlendiremiyor.")
            return

        if not any(isinstance(gate, InputGate) for gate in self.gates):
            print("Hiçbir giriş kapısı bağlı değil. Sistem değerlendiremiyor.")
            return

        if not any(lamp.is_connected_to_output_gate() for lamp in self.lamps):
            print("Çıkış kapısı herhangi bir LED'e bağlı değildir. Sistem değerlendiremiyor.")
            return

        # Doğru değerlendirme sırasını sağlamak için kapıları topolojik olarak sıralayın
        sorted_gates = self.topological_sort(self.gates)

        # Tüm kapıları doğru sırayla değerlendirin
        for gate in sorted_gates:
            gate.evaluate()

        # Lambaları güncelle
        for lamp in self.lamps:
            lamp.update_state()

    def topological_sort(self, gates):
        from collections import deque, defaultdict

        # Derece cinsinden hesapla
        in_degree = defaultdict(int)
        for gate in gates:
            for input_gate in gate.inputs:
                in_degree[gate] += 1

        # Kuyruğu sıfır dereceli kapılarla başlat
        zero_in_degree_queue = deque([gate for gate in gates if in_degree[gate] == 0])

        sorted_gates = []
        while zero_in_degree_queue:
            gate = zero_in_degree_queue.popleft()
            sorted_gates.append(gate)
            for output_gate in gate.connections:
                in_degree[output_gate.end_gate] -= 1
                if in_degree[output_gate.end_gate] == 0:
                    zero_in_degree_queue.append(output_gate.end_gate)

        return sorted_gates

    def reset_simulation(self):
        # Lambaların başlangıç durumunu ve konumunu sakla
        lamp_initial_states = [(lamp, lamp.state, (lamp.x, lamp.y)) for lamp in self.lamps]

        # Tüm giriş kapılarının ve lambaların başlangıç konumuna getir
        for gate in self.gates:
            if isinstance(gate, InputGate):
                gate.state = False
                gate.output = False
                gate.button.config(text="0")
                self.canvas.coords(gate.text, gate.x, gate.y)  # Giriş kapısının metnini başlangıç konumuna yerleştir
                self.canvas.coords(gate.connection_point, gate.x + 30, gate.y - 5, gate.x + 40,
                                   gate.y + 5)  # Bağlantı noktasını başlangıç konumuna getir
            elif isinstance(gate, Lamp):
                gate.output = False
                gate.canvas.itemconfig(gate.body, fill="red")  # Lambanın rengini kırmızıya ayarla
                gate.canvas.coords(gate.body, gate.initial_position[0],
                                   gate.initial_position[1])  # Lambayı başlangıç konumuna getir
                gate.canvas.coords(gate.text, gate.initial_position[0] + 20,
                                   gate.initial_position[1] + 50)  # Metni başlangıç konumuna yerleştir
                gate.canvas.coords(gate.connection_point, gate.initial_position[0] - 17, gate.initial_position[1] + 15,
                                   gate.initial_position[0] - 3,
                                   gate.initial_position[1] + 30)  # Bağlantı noktasını başlangıç konumuna getir

        # Lambaları başlangıç durumuna geri döndür
        for lamp, initial_state, initial_position in lamp_initial_states:
            lamp.state = initial_state
            lamp.update_state()
            lamp.x, lamp.y = initial_position

        # Tüm bağlantı noktalarını varsayılan renge geri getir
        for lamp in self.lamps:
            lamp.output = False
            lamp.canvas.itemconfig(lamp.connection_point, fill="black")

        messagebox.showinfo("Bilgi", "Simülasyon sıfırlandı.")

def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()