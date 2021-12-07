from fontParts.world import dispatcher

# from https://github.com/mekkablue/Glyphs-Scripts/blob/master/Paths/Fill%20Up%20with%20Rectangles.py
def draw_rect( bottom_left, top_right ):
    RContour = dispatcher['RContour']
    RPoint = dispatcher['RPoint']
    rect = RContour()
    coordinates = [
        [ bottom_left[0], bottom_left[1] ],
        [ top_right[0], bottom_left[1] ],
        [ top_right[0], top_right[1] ],
        [ bottom_left[0], top_right[1] ]
    ]

    for current_point in coordinates:
        point = RPoint()
        point.type = 'line'
        point.x = current_point[0]
        point.y = current_point[1]
        rect.appendPoint( point=point )

    rect.closed = True
    return rect

def draw_pixel(row_position, col_position, pixel_size):
    bottom_left = (col_position * pixel_size, row_position * pixel_size)
    top_right = ((col_position + 1) * pixel_size, (row_position + 1) * pixel_size)
    return draw_rect(bottom_left, top_right)
