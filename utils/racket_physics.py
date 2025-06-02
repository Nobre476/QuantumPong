def calculate_rebound(incoming_angle, rubber_hardness=45):
    return incoming_angle * (0.9 + rubber_hardness/500)