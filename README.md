# treemap-visualiser
Interactive visualizer GUI which displays a user’s file system hierarchy in terms of file size and performs various actions according to user input.
Expanded to support world population data from a JSON file, displaying each country in terms of population size

# Usage

In treemap_visualiser.py, at the bottom of the code in the "if __name__ == '__main__':" block, there is a call to run_treemap_file_system(PATH) and run_treemap_population().

Replace PATH with a valid path from your file system to see the file hierarchy in terms of file size.

The visualiser supports user input.
In the visualiser, you can: 
- left-click different segments to see the corresponding file name.
- right-click different segments to remove the segment from the visualiser.
- hit the up key on a segment to increase the size of the segment by 10%.
- hit the down key on a segment to decrease the size of the segment by 10%.