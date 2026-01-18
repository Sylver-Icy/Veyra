def spam_command():
    """
    Marks a command as SPAM/GRIND (allowed only in spam channels).
    """
    def decorator(func):
        setattr(func, "__channel_policy__", "spam")
        return func
    return decorator


def non_spam_command():
    """
    Marks a command as NON-SPAM (allowed only in non-spam channels).
    """
    def decorator(func):
        setattr(func, "__channel_policy__", "non_spam")
        return func
    return decorator