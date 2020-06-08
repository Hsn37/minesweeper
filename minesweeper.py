import pyglet
from random import randint
import time



ONE_BLOCK = 40		# each block is 40x40 pixels. DO NOT CHANGE

# can be tweaked. height and width must be multiples of 40.
DELAY = 0.01		# animation speed. time in ms.
HEIGHT = 480		
WIDTH = 480
BOMBS = 20

BLOCKS_VER = HEIGHT/ONE_BLOCK - 1	# no of blocks
BLOCK_HOR = WIDTH/ONE_BLOCK - 1		# no of blocks

batch2flag =  False		# flag to display bombs
reveal_flag = False		# flag for expansion of tiles
won = False
game_start = True
start_point = []
revealed = []
expandable_tiles = []
new_counter = 0
bombs_left = BOMBS


# assets for the game
window = pyglet.window.Window(WIDTH, HEIGHT, 'Minesweeper')
window.set_location(300, 100)
block_img = pyglet.resource.image('src/block.png')
bomb_img = pyglet.resource.image('src/mine.png')
flag_img = pyglet.resource.image('src/flag.png')
grey_img = pyglet.resource.image('src/grey.png')


# images for the digits
digits = []
digits.append(pyglet.resource.image('src/1.png'))
digits.append(pyglet.resource.image('src/2.png'))
digits.append(pyglet.resource.image('src/3.png'))
digits.append(pyglet.resource.image('src/4.png'))
digits.append(pyglet.resource.image('src/5.png'))
digits.append(pyglet.resource.image('src/6.png'))
digits.append(pyglet.resource.image('src/7.png'))
digits.append(pyglet.resource.image('src/8.png'))

# the 8 possible actions from one block, to reach other blocks. used to explore the area, to expand.
actions = []
actions.append([0, ONE_BLOCK])		# Up
actions.append([ONE_BLOCK, ONE_BLOCK])	# right up
actions.append([ONE_BLOCK, 0])		# right
actions.append([ONE_BLOCK, -ONE_BLOCK])	# right down
actions.append([0, -ONE_BLOCK])		# down
actions.append([-ONE_BLOCK, -ONE_BLOCK])	# left down
actions.append([-ONE_BLOCK, 0])		# left
actions.append([-ONE_BLOCK, ONE_BLOCK])	# left Up


tiles = []
bombs_array = []
bomb_sprites = []
tile_numbers = []

batch1 = pyglet.graphics.Batch()
batch2 = pyglet.graphics.Batch()


# initial blue tiles 
for i in range(0, WIDTH, ONE_BLOCK):
	for k in range(0, HEIGHT, ONE_BLOCK):
		tiles.append(pyglet.sprite.Sprite(block_img, x=i, y=k, batch=batch1))
		tile_numbers.append(0)


# randomly places a bomb. cannot place a bomb at the first block clicked. 
def define_bombs():
	global bombs_array, bomb_sprites
	n = 0
	while n < BOMBS:
		x = randint(0, BLOCK_HOR) * ONE_BLOCK
		y = randint(0, BLOCKS_VER) * ONE_BLOCK

		if bombs_array.count([x, y]) == 1 or [x, y] == start_point:
			continue
		else:
			bombs_array.append([x, y])
			bomb_sprites.append(pyglet.sprite.Sprite(img=bomb_img, x=x, y=y, batch=batch2))
			n += 1


# identifies the number each tile has. 
def define_numbers():
	global tile_numbers

	n = 0
	while n < len(tiles):
		counter = 0
		x = tiles[n].x
		y = tiles[n].y
		
		if bombs_array.count([x, y+ONE_BLOCK]) == 1:
			counter += 1
		if bombs_array.count([x+ONE_BLOCK, y+ONE_BLOCK]) == 1:
			counter += 1
		if bombs_array.count([x+ONE_BLOCK, y]) == 1:
			counter += 1
		if bombs_array.count([x+ONE_BLOCK, y-ONE_BLOCK]) == 1:
			counter += 1
		if bombs_array.count([x, y-ONE_BLOCK]) == 1:
			counter += 1
		if bombs_array.count([x-ONE_BLOCK, y-ONE_BLOCK]) == 1:
			counter += 1
		if bombs_array.count([x-ONE_BLOCK, y]) == 1:
			counter += 1
		if bombs_array.count([x-ONE_BLOCK, y+ONE_BLOCK]) == 1:
			counter += 1

		tile_numbers[n] = counter

		n += 1


# finds the index of the element in the array
def extract_index(array, element):
	for i in range(len(array)):
		if [array[i].x, array[i].y] == element:
			return i


# draws on screen
@window.event
def on_draw():
	window.clear()

	batch1.draw()
	if batch2flag == True:
		batch2.draw()

	time.sleep(DELAY)


# event handler, to handle events
@window.event
def on_mouse_press(x, y, button, modifiers):
	global game_start, start_point, batch2flag, reveal_flag, expandable_tiles, revealed, new_counter, bombs_left

	coord_x = int(x/ONE_BLOCK) * ONE_BLOCK
	coord_y = int(y/ONE_BLOCK) * ONE_BLOCK
	index = extract_index(tiles, [coord_x, coord_y])

	if not batch2flag and not won:
		if button == pyglet.window.mouse.LEFT:
			
			if game_start:
				start_point = [coord_x, coord_y]
				define_bombs()
				define_numbers()
				game_start = False

			if bombs_array.count([coord_x, coord_y]):
				print("Game Over!")
				batch2flag = True

			elif tiles[index].image == block_img or tiles[index].image == flag_img:
				if tile_numbers[index] == 0:
					tiles[index].image = grey_img
					reveal_flag = True
					new_counter = 0
					expandable_tiles = []
					expandable_tiles.append([coord_x, coord_y])

				else:
					tiles[index].image = digits[tile_numbers[index] - 1]

		if button == pyglet.window.mouse.RIGHT:
			if not game_start:
				if tiles[index].image == block_img:
					tiles[index].image = flag_img
					bombs_left -= 1
					print("Bombs left:", bombs_left)

				elif tiles[index].image == flag_img:
					tiles[index].image = block_img
					bombs_left += 1
					print("Bombs left:", bombs_left)
	else:
		window.close()


# the main program loop. 
def update(dt):
	global reveal_flag, expandable_tiles, revealed, new_counter, won

	# checking win condition
	c = 0
	for i in range(len(tiles)):
		if tiles[i].image == block_img:
			c += 1
	if c == 0:
		print("You won!")
		pyglet.clock.unschedule(update)
		won = True

	if reveal_flag:
		if new_counter < len(expandable_tiles):
			revealed.append(expandable_tiles[new_counter])

			for m in range(len(actions)):
				x1 = expandable_tiles[new_counter][0] + actions[m][0]
				y1 = expandable_tiles[new_counter][1] + actions[m][1]

				if x1 < 0 or y1 < 0 or x1 >= WIDTH or y1 >= HEIGHT:
					continue
				
				index = extract_index(tiles, [x1, y1])
				count = tile_numbers[index]

				if count == 0 and bombs_array.count([x1, y1]) != 1:
					if revealed.count([x1, y1]) < 1 and expandable_tiles.count([x1, y1]) < 1:
						expandable_tiles.append([x1, y1])
					tiles[index].image = grey_img
				else:
					tiles[index].image = digits[count - 1]

			new_counter += 1
		else:
			reveal_flag = False


print("Bombs left:", bombs_left)
pyglet.clock.schedule(update)
pyglet.app.run()