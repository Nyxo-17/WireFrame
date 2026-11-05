"""Point d'entrée unique de l'application Wireframe V1."""

from ui.app_window import WireframeApp


def main() -> None:
    """Instancie et démarre la boucle principale de la fenêtre CustomTkinter."""
    app = WireframeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
