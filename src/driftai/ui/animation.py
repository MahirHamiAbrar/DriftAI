from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve
)


class Animator:
    @staticmethod
    def animate(
        target,
        property_name,
        duration,
        start_value,
        end_value,
        easing_curve=QEasingCurve.Type.Linear
    ) -> QPropertyAnimation:

        animation = QPropertyAnimation(target, property_name.encode())
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(easing_curve)
        animation.start()
        
        return animation
