try:
    from .addon import bl_info, register, unregister
except ImportError:
    from addon import bl_info, register, unregister


__all__ = ["bl_info", "register", "unregister"]


if __name__ == "__main__":
    register()
