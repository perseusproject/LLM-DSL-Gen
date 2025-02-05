from typing import Union, List


def text_display(content: Union[str, List[str]]) -> None:
    if isinstance(content, str):
        print(content)
    else:
        for c in content:
            print(c)


def pretty_display(content: Union[str, List[str]]) -> None:
    try:
        import IPython
        from IPython.display import display, Markdown
        if IPython.get_ipython() is None:
            raise ImportError
        if isinstance(content, str):
            display(Markdown(content))
        else:
            for c in content:
                display(Markdown(c))
    except ImportError:
        text_display(content)
        pass
