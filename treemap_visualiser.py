from typing import Optional, Tuple, List

import pygame
from tree_data import FileSystemTree, AbstractTree
from population import PopulationTree


# Screen dimensions and coordinates

ORIGIN = (0, 0)
WIDTH = 1024
HEIGHT = 768
FONT_HEIGHT = 30                       # The height of the text display.
TREEMAP_HEIGHT = HEIGHT - FONT_HEIGHT  # The height of the treemap display.

# Font to use for the treemap program.
FONT_FAMILY = 'Consolas'


def run_visualisation(tree: AbstractTree) -> None:
    """Display an interactive graphical display of the given tree's treemap."""
    # Setup pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Render the initial display of the static treemap.
    render_display(screen, tree, '')

    # Start an event loop to respond to events.
    event_loop(screen, tree)


def render_display(screen: pygame.Surface, tree: AbstractTree,
                   text: str) -> None:
    """Render a treemap and text display to the given screen.

    """
    # First, clear the screen
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'],
                     (0, 0, WIDTH, HEIGHT))
    rectangles = tree.generate_treemap((0, 0, WIDTH,
                                        TREEMAP_HEIGHT))
    for rectangle in rectangles:
        pygame.draw.rect(screen, rectangle[1], rectangle[0])
    pygame.draw.rect(screen, pygame.color.THECOLORS['black'],
                     (0, TREEMAP_HEIGHT, WIDTH, FONT_HEIGHT))
    _render_text(screen, text)
    pygame.display.flip()


def _render_text(screen: pygame.Surface, text: str) -> None:
    """Render text at the bottom of the display."""
    # The font we want to use
    font = pygame.font.SysFont(FONT_FAMILY, FONT_HEIGHT - 8)
    text_surface = font.render(text, 1, pygame.color.THECOLORS['white'])

    # Where to render the text_surface
    text_pos = (0, HEIGHT - FONT_HEIGHT + 4)
    screen.blit(text_surface, text_pos)


def event_loop(screen: pygame.Surface, tree: AbstractTree) -> None:
    """Respond to events (mouse clicks, key presses) and update the display.

    Note that the event loop is an *infinite loop*: it continually waits for
    the next event, determines the event's type, and then updates the state
    of the visualisation or the tree itself, updating the display if necessary.
    This loop ends when the user closes the window.
    """
    selected_leaf = None
    while True:
        # Wait for an event
        rectangles = tree.generate_treemap((0, 0, WIDTH,
                                            TREEMAP_HEIGHT))
        rectangle_coords = []
        for rectangle in rectangles:
            rectangle_coords.append(rectangle[0])
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            this_leaf = perform_selection(selected_leaf, event.pos,
                                          rectangle_coords, screen, tree)
            selected_leaf = this_leaf
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            this_leaf = tree.get_leaf(event.pos, rectangle_coords)
            if this_leaf is not None:
                this_leaf.remove_leaf()
            info = ""
            if selected_leaf is not this_leaf and selected_leaf is not None\
                    and rectangle_coords != []:
                info = selected_leaf.get_pathname() + "  " + "(" + \
                    str(selected_leaf.data_size) + ")"
            if this_leaf is selected_leaf:
                selected_leaf = None
            render_display(screen, tree, info)
        if event.type == pygame.KEYUP and event.key == pygame.K_UP and \
                selected_leaf is not None:
            selected_leaf.increase_datasize()
            info = selected_leaf.get_pathname() + "  " + "(" + \
                str(selected_leaf.data_size) + ")"
            render_display(screen, tree, info)
        if event.type == pygame.KEYUP and event.key == pygame.K_DOWN and \
                selected_leaf is not None:
            selected_leaf.decrease_datasize()
            info = selected_leaf.get_pathname() + "  " + "(" + \
                str(selected_leaf.data_size) + ")"
            render_display(screen, tree, info)


def perform_selection(previous_leaf: Optional[AbstractTree],
                      pos: Tuple, rectangle_coords: List[Tuple],
                      screen: pygame.Surface, tree: AbstractTree) -> \
        Optional[AbstractTree]:
    """Given the previous leaf, update the screen. Return the current
    leaf.
    """
    current_selection = tree.get_leaf(pos, rectangle_coords)
    if current_selection is None or previous_leaf is current_selection:
        render_display(screen, tree, "")
        return None
    if previous_leaf is None or current_selection is not previous_leaf:
        info = current_selection.get_pathname() + "  " + "(" + \
            str(current_selection.data_size) + ")"
        render_display(screen, tree, info)
        return current_selection
    return None


def run_treemap_file_system(path: str) -> None:
    """Run a treemap visualisation for the given path's file structure.

    Precondition: <path> is a valid path to a file or folder.
    """
    file_tree = FileSystemTree(path)
    run_visualisation(file_tree)


def run_treemap_population() -> None:
    """Run a treemap visualisation for World Bank population data."""
    pop_tree = PopulationTree(True)
    run_visualisation(pop_tree)


if __name__ == '__main__':
    # Can only run the file hierarchy visualizer or population visualizer one at
    # a time. Comment the other one out.

    # the following is a valid path in my Mac
    # replace this path with a valid path in your system
    # run_treemap_file_system('/Users/humjot/Desktop/Dev/treemap visualiser')

    run_treemap_population()

