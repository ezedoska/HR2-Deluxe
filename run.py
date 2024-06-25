from ast import Load
from textual.app import App, ComposeResult
from textual.widgets import RichLog, Button, LoadingIndicator, Checkbox,Static
from textual.containers import VerticalScroll, Container, Vertical
from PIL import Image
from rich_pixels import Pixels
from procs import (
    SOMOSO,
    TADI,
    Remanentes,
    memes,
    Keys,
    SintysStats,
    PaquetesSINTyS,
    noms,
    SumarPagos,
    Paquetes2Excel as p2e
)
from textual_pandas.widgets import DataFrameTable
from textual import work
import pandas as pd
import random
import os
import traceback
from textual_serve.server import Server


class HR2(App):
    CSS_PATH = "utility_containers.tcss"
    BINDINGS = [
        ("ctrl+b", "toggle_sidebar", "Sidebar"),
    ]
    computer = os.environ["COMPUTERNAME"]
    if "118" or "2k" in computer.lower():
        user = "Eze"
    elif "051":
        user = "Juanchi"
    else:
        user = "Extraño"
    df = pd.read_csv("paquetelog.txt", sep="|").sort_values(
        by="FECHA_PROCESO", ascending=False
    )

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#hov")
        self.set_focus(None)
        if sidebar.has_class("-hidden"):
            sidebar.remove_class("-hidden")
        else:
            if sidebar.query("*:focus"):
                self.screen.set_focus(None)
            sidebar.add_class("-hidden")

    def on_mount(self):
        self.action_toggle_sidebar()
        self.screen.border_title = (
            f"[HERRAMIENTAS REDLES 2 DELUXE]"
        )
        self.screen.border_subtitle = (
            f"{self.computer} - ¡Hola {self.user}! {random.choice(memes.redleshello)}"
        )
        table = self.query_one(DataFrameTable)
        table.add_df(self.df)
        table.zebra_stripes = True

    def compose(self) -> ComposeResult:
        with Image.open("pixil-frame-0.png") as image:
            pixels = Pixels.from_image(image)
        vm = VerticalScroll(id="Menu")
        vm.border_title = "MENU"
        with vm:
            procs = Container(classes="cont")
            procs.border_title = "[PROC DATOS]"
            with procs:
                yield Button("SOMOSO", id="somoso", classes="botones")
                yield Button("TADI", id="tadi", classes="botones")
                yield Button("Remanentes", id="remanentes", classes="botones")
                yield Button("NOMS", id="noms", classes="botones")
            crypto = Container(classes="cont")
            crypto.border_title = "[CRYPTO]"
            with crypto:
                yield Button("Desencriptar", id="desencriptar", classes="botones")
                yield Button("Encriptar", id="encriptar", classes="botones")
                yield Button("Instalar Keys", id="inskeys", classes="botones")
            stats = Container(classes="cont")
            stats.border_title = "[STATS]"
            with stats:
                yield Button("Sumar Pagos", id="sumarpagos", classes="botones")
                yield Button("Morosos", id="morosos", classes="botones")
            sintcont = Container(classes="cont")
            sintcont.border_title = "[SINTyS]"
            with sintcont:
                yield Button("SINTyS eval/proc", id="sintys", classes="botones")
                yield Checkbox("Pd 2.0", id="ver",classes="check")
                yield Checkbox("Xls JUB",id="jubi",classes="check")
                yield Checkbox("Xls EVAL",id="eval", classes="check")
                yield Checkbox("Xls DAT",id="datos", classes="check")
            txt2xls = Container(classes="cont")
            txt2xls.border_title = "[TXT > XLSX]"
            with txt2xls:
                yield Button("F1252", id="f1252", classes="botones")
                yield Button("F1252v", id="f1252v", classes="botones")
                yield Button("F1253v", id="f1253v", classes="botones")
                yield Button("F1257", id="f1257", classes="botones")
                yield Button("F1258", id="f1258", classes="botones")
                yield Button("SOMOSO", id="somosox", classes="botones")
        self.rl = RichLog(highlight=True, markup=True, id="log", wrap=True)
        self.rl.border_title = "LOG"
        yield self.rl
        dft = DataFrameTable(id="tabla")
        dft.border_title = "PROC LOG"
        yield Static(pixels,id="img")
        yield dft
        li = LoadingIndicator(id="load", classes="-hidden")
        with Vertical(id="hov"):
            yield li
        # yield Header()
        # yield Footer()

    def on_ready(self) -> None:
        """Called  when the DOM is ready."""

    @work(exclusive=True, thread=True)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.action_toggle_sidebar()
        self.query_one("#Menu").disabled = True
        log = self.query_one("#log")
        try:
            if event.button.id == "somoso":
                SOMOSO.run(log)
            if event.button.id == "tadi":
                TADI.run(log)
            if event.button.id == "remanentes":
                Remanentes.run(log)
            if event.button.id == "noms":
                noms.run(log)
            if event.button.id == "inskeys":
                Keys.run(log)
            if event.button.id == "desencriptar":
                PaquetesSINTyS.runDecrypt(log)
            if event.button.id == "encriptar":
                PaquetesSINTyS.runEncrypt(log)
            if event.button.id == "sumarpagos":
                SumarPagos.run(log)
            if event.button.id == "sintys":
                version = self.query_one("#ver").value
                jubi = self.query_one("#jubi").value
                eval = self.query_one("#eval").value
                datos = self.query_one("#datos").value
                SintysStats.run(log,version,jubi,eval,datos)
            if event.button.id == "f1252":
                p2e.p02xlsx(log)
            if event.button.id == "f1252v":
                p2e.p12xlsx(log)
            if event.button.id == "f1253v":
                p2e.p52xlsx(log)
            if event.button.id == "f1257":
                p2e.p72xlsx(log)
            if event.button.id == "f1258":
                p2e.p82xlsx(log)
            if event.button.id == "somosox":
                p2e.somoso2xlsx(log)
            df = pd.read_csv("paquetelog.txt", sep="|").sort_values(
                by="FECHA_PROCESO", ascending=False
            )
            self.query_one(DataFrameTable).update_df(df)
            self.query_one("#Menu").disabled = False
            self.action_toggle_sidebar()
        except Exception as e:
            # log.write(f"Error: {e.__class__.__name__} - {e}")
            # log.write(mostrar_linea_de_error(e))
            log.app.copy_to_clipboard(str(traceback.format_exc()))
            log.write(
                traceback.format_exc() + "\nEl error fue copiado al portapapeles."
            )
            self.query_one("#Menu").disabled = False
            self.action_toggle_sidebar()

if __name__ == "__main__":
    app = HR2().run()