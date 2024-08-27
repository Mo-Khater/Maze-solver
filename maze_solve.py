import random
from PIL import Image, ImageDraw

def parse_maze(filename):
    with open(filename, 'r') as file:
        maze = [list(line.rstrip()) for line in file.readlines()]

    # To make all rows the same length
    max_len = max(len(row) for row in maze)
    for row in maze:
        row.extend(' ' * (max_len - len(row)))
    return maze


def maze_to_image(maze, final_path=None, cell_size=50, output_file='maze_solution.png'):
    rows = len(maze)
    columns = len(maze[0])

    img_width = columns * cell_size
    img_height = rows * cell_size

    # Create a blank white image
    image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(image)

    border_color = 'black'


    # Draw the maze
    for i in range(rows):
        for j in range(columns):
            color = 'white'
            if maze[i][j] == '#':
                color = (40, 40, 40)
            elif maze[i][j] == 'A':
                color = (0, 171, 28)
            elif maze[i][j] == 'B':
                color = (255, 0, 0)
            elif maze[i][j] == 'o':  # This is the final path
                color = (220, 235, 113)

            top_left = (j * cell_size, i * cell_size)
            bottom_right = ((j + 1) * cell_size, (i + 1) * cell_size)
            draw.rectangle([top_left, bottom_right], fill=color, outline=border_color, width=3)


    if final_path:
        for i, step in enumerate(final_path): #each step is cell coordinates (row, column)
            top_left = (step[1] * cell_size, step[0] * cell_size) #zero --> row - y, 1--> column - x
            bottom_right = ((step[1] + 1) * cell_size, (step[0] + 1) * cell_size)

            if i == 0:  # First step
                draw.rectangle([top_left, bottom_right], fill=(255, 0, 0), outline=border_color, width=3)
            elif i == len(final_path) - 1:  # Last step
                draw.rectangle([top_left, bottom_right], fill=(0, 171, 28), outline=border_color, width=3)
            else:  # Intermediate steps
                draw.rectangle([top_left, bottom_right], fill=(220, 235, 113), outline=border_color, width=3)

    # Save the image
    image.save(output_file)
    image.show()


def find_start_and_end(maze):
    start, end = None, None
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == 'A':
                start = (i, j)
            elif maze[i][j] == 'B':
                end = (i, j)
    return start, end


def generate_population(start, end, pop_size, maze, rows, columns):
    population = []
    for _ in range(pop_size):
        path = []
        current = start
        path.append(current)
        while current != end:
            move = random.choice(['N', 'S', 'E', 'W'])
            next_step = current
            if move == 'N' and current[0] > 0 and maze[current[0] - 1][current[1]] != '#':
                next_step = (current[0] - 1, current[1])
            elif move == 'S' and current[0] < rows - 1 and maze[current[0] + 1][current[1]] != '#':
                next_step = (current[0] + 1, current[1])
            elif move == 'E' and current[1] < columns - 1 and maze[current[0]][current[1] + 1] != '#':
                next_step = (current[0], current[1] + 1)
            elif move == 'W' and current[1] > 0 and maze[current[0]][current[1] - 1] != '#':
                next_step = (current[0], current[1] - 1)

            if next_step != current:  # Ensuring no loops
                current = next_step
                path.append(current)
        population.append(path)
    return population


def fitness(path, end):
    distance_to_end = abs(end[0] - path[-1][0]) + abs(end[1] - path[-1][1]) #manhattan distance abs(y difference) + abs(x difference)
    return 1 / (len(path) + distance_to_end) #shorter paths are better -- lamma na3mel 1 over path so8ayyar 7aykoon el fitness bta3o akbar


def mutate(path, maze, end, rows, columns): #maze is a 2D array
    index = random.randint(1, len(path) - 2) #me4 3ayzeen ne8ayyar el end wala el start
    path = path[:index] #selects the first portion of a random path
    current = path[-1]
    while current != end:
        move = random.choice(['N', 'S', 'E', 'W'])
        next_step = current
        if move == 'N' and current[0] > 0 and maze[current[0] - 1][current[1]] != '#':
            next_step = (current[0] - 1, current[1])
        elif move == 'S' and current[0] < rows - 1 and maze[current[0] + 1][current[1]] != '#':
            next_step = (current[0] + 1, current[1])
        elif move == 'E' and current[1] < columns - 1 and maze[current[0]][current[1] + 1] != '#':
            next_step = (current[0], current[1] + 1)
        elif move == 'W' and current[1] > 0 and maze[current[0]][current[1] - 1] != '#':
            next_step = (current[0], current[1] - 1)

        if next_step != current:  # Ensuring no loops
            current = next_step
            path.append(current)
    return path


def crossover(parent1, parent2):
    min_len = min(len(parent1), len(parent2))
    for i in range(1, min_len):
        if parent1[i] == parent2[i]:
            continue
        else:
            return parent1[:i] + parent2[i:] #beya5odd goz2 men da we goz2 men da
    return parent1[:min_len]  # Default to taking the path up to the minimum length


def genetic_algorithm(maze, start, end, pop_size=400, generations=100):
    rows, columns = len(maze), len(maze[0])
    population = generate_population(start, end, pop_size, maze, rows, columns)

    for generation in range(generations):
        population = sorted(population, key=lambda x: fitness(x, end), reverse=True) #a3la fitness a7san 7aga -- maximizing

        if fitness(population[0], end) == 1:
            print(f"Solution found in generation {generation}")
            return population[0]

        next_population = population[:pop_size // 2] #the top half beykamel ma3ana

        while len(next_population) < pop_size:
            parent1 = random.choice(population[:pop_size // 4])
            parent2 = random.choice(population[:pop_size // 4])
            child = crossover(parent1, parent2)
            next_population.append(mutate(child, maze, end, rows, columns))

        population = next_population

    return population[0]  # Return the best solution found


# Main execution
maze = parse_maze('maze.txt')
start, end = find_start_and_end(maze)
final_path = genetic_algorithm(maze, start, end)


# Mark the solution on the maze
maze_solution = [row[:] for row in maze]
for step in final_path:
    maze_solution[step[0]][step[1]] = 'o'

maze_to_image(maze_solution, final_path)



