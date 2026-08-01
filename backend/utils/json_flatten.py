def flatten_dict(d: dict, prefix: str = "", sep: str = " ") -> str:
    """Recursively flatten a nested dict into a plain text string for embedding."""
    parts = []
    for key, value in d.items():
        label = f"{prefix}{key}" if prefix else key
        if isinstance(value, dict):
            parts.append(flatten_dict(value, prefix=f"{label}.", sep=sep))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parts.append(flatten_dict(item, prefix=f"{label}.", sep=sep))
                else:
                    parts.append(f"{label}: {item}")
        else:
            parts.append(f"{label}: {value}")
    return sep.join(parts)
