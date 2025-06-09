from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp
import json
import os
import random

Window.clearcolor = (0.1, 0.1, 0.2, 1)  # Fondo oscuro

class LootApp(App):
    def build(self):
        self.boss_data = self.load_data()
        self.setup_ui()
        return self.layout

    def setup_ui(self):
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Título
        self.title_label = Label(
            text="[color=#FFD700]Sistema de Loot RPG[/color]",
            markup=True,
            font_size=dp(24),
            size_hint=(1, 0.1))
        
        # Selector de Boss
        self.boss_spinner = Spinner(
            text='Selecciona un Boss' if self.boss_data else 'No hay bosses',
            values=list(self.boss_data.keys()) if self.boss_data else [],
            font_size=dp(20),
            size_hint=(1, 0.1),
            background_color=(0.3, 0.3, 0.5, 1))
        
        # Botón Generar Loot
        self.btn_generate = Button(
            text="Generar Loot",
            background_color=(0, 0.7, 0, 1),
            font_size=dp(20),
            size_hint=(1, 0.1),
            on_press=self.generate_loot)
        
        # Botones de Gestión
        btn_grid = GridLayout(cols=3, spacing=dp(5), size_hint=(1, 0.1))
        btn_grid.add_widget(Button(
            text="Añadir Boss",
            background_color=(0.2, 0.5, 1, 1),
            on_press=self.show_add_popup))
        btn_grid.add_widget(Button(
            text="Editar Loot",
            background_color=(0.8, 0.5, 0, 1),
            on_press=self.show_edit_popup))
        btn_grid.add_widget(Button(
            text="Eliminar Boss",
            background_color=(0.9, 0.2, 0.2, 1),
            on_press=self.show_delete_popup))
        
        # Área de Resultados con Scroll
        scroll_results = ScrollView(size_hint=(1, 0.6))
        self.result_label = Label(
            text="[color=#FFFFFF]Selecciona un boss...[/color]",
            markup=True,
            font_size=dp(18),
            size_hint_y=None,
            halign='center',
            valign='top',
            text_size=(Window.width - dp(20), None))
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        scroll_results.add_widget(self.result_label)
        
        # Ensamblar UI
        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.boss_spinner)
        self.layout.add_widget(self.btn_generate)
        self.layout.add_widget(btn_grid)
        self.layout.add_widget(scroll_results)

    def load_data(self):
        if os.path.exists('boss_data.json'):
            with open('boss_data.json', 'r') as f:
                return json.load(f)
        return {"Dragón Ancestral": ["Espada del Abismo"], "Rey Esqueleto": ["Hueso Maldito"]}

    def save_data(self):
        with open('boss_data.json', 'w') as f:
            json.dump(self.boss_data, f)

    def generate_loot(self, instance):
        boss = self.boss_spinner.text
        if boss in self.boss_data and self.boss_data[boss]:
            loot = random.sample(self.boss_data[boss], min(3, len(self.boss_data[boss])))
            self.result_label.text = f"[color=#00FF00]Loot de {boss}:[/color]\n\n" + "\n".join(f"• {item}" for item in loot)
        else:
            self.result_label.text = "[color=#FF0000]¡Este boss no tiene items![/color]"

    def show_add_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text="Nombre del nuevo boss:", size_hint=(1, 0.2)))
        
        self.new_boss_input = TextInput(multiline=False, size_hint=(1, 0.2))
        content.add_widget(self.new_boss_input)
        
        btn_layout = BoxLayout(spacing=dp(5), size_hint=(1, 0.2))
        btn_layout.add_widget(Button(
            text="Cancelar",
            on_press=lambda x: self.popup.dismiss()))
        btn_layout.add_widget(Button(
            text="Añadir",
            on_press=self.add_boss))
        
        content.add_widget(btn_layout)
        self.popup = Popup(title="Añadir Boss", content=content, size_hint=(0.8, 0.4))
        self.popup.open()

    def add_boss(self, instance):
        new_boss = self.new_boss_input.text.strip()
        if new_boss and new_boss not in self.boss_data:
            self.boss_data[new_boss] = []
            self.save_data()
            self.boss_spinner.values = list(self.boss_data.keys())
            self.boss_spinner.text = new_boss
            self.result_label.text = f"[color=#00FF00]¡Boss {new_boss} añadido![/color]"
        self.popup.dismiss()

    def show_edit_popup(self, instance):
        boss = self.boss_spinner.text
        if boss not in self.boss_data:
            return
            
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text=f"Editando loot de {boss}:", size_hint=(1, 0.1)))
        
        # ScrollView para items existentes
        scroll = ScrollView(size_hint=(1, 0.6), do_scroll_x=False)
        grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for item in self.boss_data[boss]:
            item_label = Label(
                text=f"• {item}",
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='middle',
                markup=True
            )
            grid.add_widget(item_label)
        
        scroll.add_widget(grid)
        content.add_widget(scroll)
        
        # Añadir nuevo item
        self.new_item_input = TextInput(
            hint_text="Escribe un nuevo item",
            size_hint=(1, 0.1),
            multiline=False
        )
        content.add_widget(self.new_item_input)
        
        btn_layout = BoxLayout(spacing=dp(5), size_hint=(1, 0.2))
        btn_layout.add_widget(Button(
            text="Cancelar",
            on_press=lambda x: self.popup.dismiss()))
        btn_layout.add_widget(Button(
            text="Añadir Item",
            on_press=lambda x: self.add_item(boss)))
        btn_layout.add_widget(Button(
            text="Guardar",
            on_press=lambda x: self.save_loot(boss)))
        
        content.add_widget(btn_layout)
        self.popup = Popup(title=f"Editando: {boss}", content=content, size_hint=(0.9, 0.8))
        self.popup.open()

    def add_item(self, boss):
        new_item = self.new_item_input.text.strip()
        if new_item:
            self.boss_data[boss].append(new_item)
            self.new_item_input.text = ""
            # Actualizar la vista del popup
            self.show_edit_popup(None)  # None porque no usamos el 'instance' aquí

    def save_loot(self, boss):
        self.save_data()
        self.popup.dismiss()
        self.result_label.text = f"[color=#00FF00]¡Loot de {boss} guardado![/color]"

    def show_delete_popup(self, instance):
        boss = self.boss_spinner.text
        if boss not in self.boss_data:
            return
            
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(
            text=f"¿Eliminar a {boss} permanentemente?",
            font_size=dp(18),
            size_hint=(1, 0.6)))
        
        btn_layout = BoxLayout(spacing=dp(5), size_hint=(1, 0.3))
        btn_layout.add_widget(Button(
            text="Cancelar",
            on_press=lambda x: self.popup.dismiss()))
        btn_layout.add_widget(Button(
            text="Eliminar",
            background_color=(0.9, 0.2, 0.2, 1),
            on_press=lambda x: self.delete_boss(boss)))
        
        content.add_widget(btn_layout)
        self.popup = Popup(title="Confirmar Eliminación", content=content, size_hint=(0.7, 0.4))
        self.popup.open()

    def delete_boss(self, boss):
        del self.boss_data[boss]
        self.save_data()
        self.boss_spinner.values = list(self.boss_data.keys()) if self.boss_data else []
        self.boss_spinner.text = 'No hay bosses' if not self.boss_data else self.boss_spinner.values[0]
        self.popup.dismiss()
        self.result_label.text = f"[color=#FF0000]¡Boss {boss} eliminado![/color]"

if __name__ == '__main__':
    LootApp().run()
