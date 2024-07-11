import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1OPeA9U9P1rw0ZIIQmX-Ms7mZ6A6RH7waUXpLr8QuIfM"
SAMPLE_RANGE_NAME = "Página1!A1:K49"


categorias = {
    1: ["Hamburguer", "X-Burguer", "X-Bacon", "X-Frango", "X-Calabresa", "X-Salsicha", "X-Tudo", "X-Tudão", "Egg Burguer", "X-Egg Burguer", "X-Egg Bacon", "X-Egg Calabresa", "X-Egg Frango", "X-Egg Frango c/ Bacon", "X-Egg Frango c/ Calabresa", "Misto", "Bauru", "Sanduiche de Queijo", "Americano", "American Burguer"],
    2: ["Salgados", "Coxinha", "Coxinha c/ Catupiry", "Enroladinho", "Pastel", "Pizza", "Empada", "Cachorro-Quente", "Torta de Frango"],
    3: ["Doces", "Fatia de Bolo", "Bolo de Noiva", "Açaí 300ml", "Açaí 500ml", "Guaraná do Amazonas", "Milk-Shake"],
    4: ["Bebidas", "Coca-Cola 200ml", "Coca-Cola 290ml", "Coca-Cola 1L", "Coca-Cola 2L", "Coca-Cola Retornável", "Antarctica 1L", "Antarctica 2L", "Fanta 1L", "Fanta 2L", "Refri Lata", "Refri 200ml", "Suco da Polpa c/ Leite", "Suco da Polpa sem Leite"],
    5: ["Voltar"]
}


precos = {
    "Hamburguer": 7.00, "X-Burguer": 9.00, "X-Bacon": 13.00, "X-Frango": 14.00, "X-Calabresa": 14.00,
    "X-Salsicha": 10.00, "X-Tudo": 19.50, "X-Tudão": 33.00, "Egg Burguer": 8.00, "X-Egg Burguer": 10.00,
    "X-Egg Bacon": 16.00, "X-Egg Calabresa": 16.00, "X-Egg Frango": 16.00, "X-Egg Frango c/ Bacon": 19.00,
    "X-Egg Frango c/ Calabresa": 19.00, "Misto": 7.00, "Bauru": 8.00, "Sanduiche de Queijo": 7.00,
    "Americano": 11.00, "American Burguer": 13.00, "Coxinha": 4.00, "Coxinha c/ Catupiry": 4.00,
    "Enroladinho": 4.00, "Pastel": 8.00, "Pizza": 7.00, "Empada": 5.00, "Cachorro-Quente": 6.00,
    "Torta de Frango": 9.00, "Fatia de Bolo": 9.00, "Bolo de Noiva": 15.00, "Açaí 300ml": 10.00, "Açaí 500ml": 14.00,
    "Guaraná do Amazonas": 6.00, "Milk-Shake": 14.00, "Coca-Cola 200ml": 3.50, "Coca-Cola 290ml": 5.00,
    "Coca-Cola 1L": 9.00, "Coca-Cola 2L": 14.00, "Coca-Cola Retornável": 8.00, "Antarctica 1L": 8.00,
    "Antarctica 2L": 10.00, "Fanta 1L": 9.00, "Fanta 2L": 14.00, "Refri Lata": 6.00, "Refri 200ml": 2.50,
    "Suco da Polpa c/ Leite": 7.00, "Suco da Polpa sem Leite": 6.00
}


def salvar_historico(pedidos):
    historico = carregar_historico()
    historico.extend(pedidos)
    with open("historico_pedidos.json", "w") as file:
        json.dump(historico, file)


def carregar_historico():
    try:
        with open("historico_pedidos.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def salvar_historico_google_sheets(pedidos):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r"D:\YouStore\Code\credenciais.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
       
        with open("token.json", "w") as token:
            token.write(creds.to_json())


    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()


        def atualizar_quantidade_google_sheets(item, cell_range):
            total_quantity = sum(pedido["quantidade"] for pedido in pedidos if pedido["item"] == item)
            if total_quantity > 0:
                result = sheet.values().get(
                    spreadsheetId=SAMPLE_SPREADSHEET_ID, range=cell_range
                ).execute()
                current_quantity = result.get("values", [[0]])[0][0]


                try:
                    current_quantity = int(current_quantity)
                except ValueError:
                    current_quantity = 0


                total_quantity += current_quantity
                print(f"Atualizando {cell_range}: Quantidade atual = {current_quantity}, Adicionando = {total_quantity - current_quantity}, Nova quantidade = {total_quantity}")


                sheet.values().update(
                    spreadsheetId=SAMPLE_SPREADSHEET_ID,
                    range=cell_range,
                    valueInputOption="USER_ENTERED",
                    body={"values": [[total_quantity]]},
                ).execute()


        # Atualiza as quantidades de X-Burguer e X-Bacon
        atualizar_quantidade_google_sheets("X-Burguer", "Página1!F3")
        atualizar_quantidade_google_sheets("X-Bacon", "Página1!F4")
        atualizar_quantidade_google_sheets("X-Frango", "Página1!F5")
        atualizar_quantidade_google_sheets("X-Calabresa", "Página1!F6")
        atualizar_quantidade_google_sheets("X-Salsicha", "Página1!F7")
        atualizar_quantidade_google_sheets("X-Tudo", "Página1!F8")
        atualizar_quantidade_google_sheets("X-Tudão", "Página1!F9")
        atualizar_quantidade_google_sheets("Egg Burguer", "Página1!F10")
        atualizar_quantidade_google_sheets("X-Egg Burguer", "Página1!F11")
        atualizar_quantidade_google_sheets("X-Egg Bacon", "Página1!F12")
        atualizar_quantidade_google_sheets("X-Egg Calabresa", "Página1!F13")
        atualizar_quantidade_google_sheets("X-Egg Frango", "Página1!F14")
        atualizar_quantidade_google_sheets("X-Egg Frango c/ Bacon", "Página1!F15")
        atualizar_quantidade_google_sheets("X-Egg Frango c/ Calabresa", "Página1!F16")
        atualizar_quantidade_google_sheets("Misto", "Página1!F17")
        atualizar_quantidade_google_sheets("Bauru", "Página1!F18")
        atualizar_quantidade_google_sheets("Sanduíche de Queijo", "Página1!F19")
        atualizar_quantidade_google_sheets("Americano", "Página1!F20")
        atualizar_quantidade_google_sheets("American Burguer", "Página1!F21")
        atualizar_quantidade_google_sheets("Coxinha", "Página1!F22")
        atualizar_quantidade_google_sheets("Coxinha c/ Catupiry", "Página1!F23")
        atualizar_quantidade_google_sheets("Enroladinho", "Página1!F24")
        atualizar_quantidade_google_sheets("Pastel", "Página1!F25")
        atualizar_quantidade_google_sheets("Pizza", "Página1!F26")
        atualizar_quantidade_google_sheets("Empada", "Página1!F27")
        atualizar_quantidade_google_sheets("Cachorro-Quente", "Página1!F28")
        atualizar_quantidade_google_sheets("Torta de Frango", "Página1!F29")
        atualizar_quantidade_google_sheets("Fatia de Bolo", "Página1!F30")
        atualizar_quantidade_google_sheets("Bolo de Noiva", "Página1!F31")
        atualizar_quantidade_google_sheets("Açaí 300ml", "Página1!F32")
        atualizar_quantidade_google_sheets("Açaí 500ml", "Página1!F33")
        atualizar_quantidade_google_sheets("Guaraná do Amazonas", "Página1!F34")
        atualizar_quantidade_google_sheets("Milk-Shake", "Página1!F35")
        atualizar_quantidade_google_sheets("Coca-Cola 200ml", "Página1!F36")
        atualizar_quantidade_google_sheets("Coca-Cola 290ml", "Página1!F37")
        atualizar_quantidade_google_sheets("Coca-Cola 1L", "Página1!F38")
        atualizar_quantidade_google_sheets("Coca-Cola 2L", "Página1!F39")
        atualizar_quantidade_google_sheets("Coca-Cola Retornável", "Página1!F40")
        atualizar_quantidade_google_sheets("Antarctica 1L", "Página1!F41")
        atualizar_quantidade_google_sheets("Antarctica 2L", "Página1!F42")
        atualizar_quantidade_google_sheets("Fanta 1L", "Página1!F43")
        atualizar_quantidade_google_sheets("Fanta 2L", "Página1!F44")
        atualizar_quantidade_google_sheets("Refri Lata", "Página1!F45")
        atualizar_quantidade_google_sheets("Refri 200ml", "Página1!F46")
        atualizar_quantidade_google_sheets("Suco da Polpa c/ Leite", "Página1!F47")
        atualizar_quantidade_google_sheets("Suco da Polpa sem Leite", "Página1!F48")


        # Salva os pedidos no Google Sheets
        valores_adicionar = [[pedido["item"], pedido["quantidade"], pedido["total"]] for pedido in pedidos]
        body = {'values': valores_adicionar}
        sheet.values().append(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range="Página1!A2",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()


    except HttpError as err:
        print(err)


class PedidoApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10


        self.categoria_spinner = Spinner(
            text='Escolha a categoria',
            values=[categorias[key][0] for key in categorias.keys() if categorias[key]]
        )
        self.add_widget(self.categoria_spinner)


        self.item_spinner = Spinner(
            text='Escolha o item',
            values=[]
        )
        self.categoria_spinner.bind(text=self.on_categoria_select)
        self.add_widget(self.item_spinner)


        self.quantidade_input = TextInput(text='1', multiline=False, input_filter='int')
        self.add_widget(Label(text='Quantidade:'))
        self.add_widget(self.quantidade_input)


        self.button_add = Button(text='Adicionar ao pedido')
        self.button_add.bind(on_press=self.add_to_pedido)
        self.add_widget(self.button_add)


        self.button_historico = Button(text='Ver Histórico')
        self.button_historico.bind(on_press=self.ver_historico)
        self.add_widget(self.button_historico)


        self.pedidos = []
        self.label_total = Label(text='Total: R$ 0.00')
        self.add_widget(self.label_total)


    def on_categoria_select(self, spinner, text):
        categoria_id = next(key for key, value in categorias.items() if value and value[0] == text)
        self.item_spinner.values = categorias[categoria_id][1:]


    def add_to_pedido(self, instance):
        item = self.item_spinner.text
        quantidade = int(self.quantidade_input.text)
        preco_unitario = precos.get(item, 0)
        total_item = quantidade * preco_unitario
        self.pedidos.append({"item": item, "quantidade": quantidade, "total": total_item})
        total_geral = sum(pedido["total"] for pedido in self.pedidos)
        self.label_total.text = f'Total: R$ {total_geral:.2f}'
        salvar_historico(self.pedidos)
        salvar_historico_google_sheets(self.pedidos)
        self.pedidos.clear()


    def ver_historico(self, instance):
        historico = carregar_historico()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for pedido in historico:
            label = Label(text=f'{pedido["quantidade"]}x {pedido["item"]} - R$ {pedido["total"]:.2f}', size_hint_y=None, height=40)
            layout.add_widget(label)


        scroll = ScrollView(size_hint=(1, None), size=(400, 400))
        scroll.add_widget(layout)


        popup = Popup(title='Histórico de Pedidos', content=scroll, size_hint=(0.9, 0.9))
        popup.open()


class NickBurgerApp(App):
    def build(self):
        return PedidoApp()


if __name__ == '__main__':
    NickBurgerApp().run()
