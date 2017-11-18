from tandem.executables.agent import TandemAgent


def main():
    with TandemAgent() as agent:
        print("Tandem Agent started. Press Ctrl-D to exit.")


if __name__ == "__main__":
    main()
