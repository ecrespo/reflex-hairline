import reflex as rx

config = rx.Config(
    app_name="hairline_demo",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="inherit", accent_color="gray", gray_color="slate", radius="medium"),
        ),
    ],
)
