from buzzbot.buzzcli import parse_args, repl, run_hello_test, repl_multiline
from buzzbot.config import AppConfig
from buzzbot.io_utils import save_history, load_history, print_message, colorize
from buzzbot.chat import ChatSession

from pathlib import Path
from agents import set_default_openai_key



def main():
    # Parse command line arguments
    args = parse_args()

    # Load configuration from environment or .env file
    try:
        config = AppConfig.load()
        set_default_openai_key(config.openai_api_key)
    except RuntimeError as e:
        print(f"[error] {e}\nSet OPENAI_API_KEY and other params in environment or .env.")
        return 1
    if args.no_color:
        config.color = False
    if args.system:
        config.system_prompt = args.system

    # If only testing the API, do that and exit before interactive setup.
    if getattr(args, 'test_openai', False):
        return run_hello_test(config)

    history = []
    if args.session:
        p = Path(args.session)
        if p.exists():
            history = load_history(p)
            print(f"Loaded {len(history)} messages from {p}")
        else:
            print(f"[warn] Session file not found: {p}")

    session = ChatSession(config=config, history=history)

    if args.multiline:
        repl_multiline(session)
    else:
        repl(session)

    return 0


if __name__ == "__main__":
    main()
