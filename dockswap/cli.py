import typer


app = typer.Typer()


@app.command()
def dummy():
    typer.echo("Dummy")


if __name__ == "__main__":
    app()
