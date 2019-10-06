import tkinter as tk
import time, random, math
from copy import deepcopy
from copy import copy
import ujson


root = tk.Tk()
width = 300
height = 600
canvas = tk.Canvas(root, width=width, height=height)
canvas.pack()

fps = 6  # times 2 because lineclear in different frame
pps = 6.5 #line 278

tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]


colors = [
    (0,   0,   0  ),
    (180, 0,   255),
    (0,   150, 0  ),
    (255, 0,   0  ),
    (0,   0,   255),
    (255, 120, 0  ),
    (0,   220, 220),
    (255, 255, 0  )
]

def rotate_clockwise(shape):
	return [ [ shape[y][x]
			for y in range(len(shape)) ]
		for x in range(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, piece, x):
    piece_height = len(piece)
    piece_width = len(piece[0])

    square = False
    if piece_height == piece_width:
        square=True

    end_y = 20-piece_height # working

    for i in range(20-piece_height, -1, -1): #going down the board till we hit floor or piece
        for j in range(0, piece_height*piece_width):
            current_width = j%piece_width
            if square:
                if j<2:
                    current_height = 0
                else:
                    current_height = 1
            else:
                current_height = j%piece_height
            if board[i+current_height][x+current_width] != 0 and piece[current_height][current_width] != 0:   #board [y][x]
                end_y = i-1
                break
    return end_y

class Tetrisboard:
    def __init__(self):
        self.board =  [[0 for i in range(10)] for i in range(20)]

    def printboard(self):
        for i in range(20):
            print(self.board[i], i)
    
    def setboard(self, board):
        #self.board = deepcopy(board)
        self.board = ujson.loads(ujson.dumps(board))
    
    def getboard(self):
        return self.board
    
    def resetboard(self):
        self.board =  [[0 for i in range(10)] for i in range(20)]
    
    def drawboard(self):
        for i in range(0, 20):
            for j in range(0, 10):
                #if self.board[i][j] != 0:
                color = '#%02x%02x%02x' % colors[self.board[i][j]]
                canvas.create_rectangle(j*width/10, i*height/20, j*width/10+width/10, i*height/20+height/20, outline="#000000", fill=color)
                
    
    def add_piece(self, piece_id, x, rotation):  # x is absolute x-axis position on board
        piece = tetris_shapes[piece_id]
        for i in range(rotation):
                piece = rotate_clockwise(piece)
        piece_height = len(piece)
        piece_width = len(piece[0])

        if(x+piece_width > 9):
            x = 9-piece_width+1

        end_y = check_collision(self.board, piece, x)

        for i in range(0, piece_height):
            for j in range(0, piece_width):
                self.board[end_y+i][x+j] += piece[i][j]

        return end_y

    def holecount(self, last_y):
        holes = 0

        for i in range(last_y, 20-1):
            for j in range(0, 10):
                if self.board[i][j] != 0 and self.board[i+1][j] == 0:
                    holes += 1
        return holes

    def skyline(self):
        top_pieces = []
        for i in range(0, 10):
            for j in range(0, 20):
                if self.board[j][i] != 0:
                    top_pieces.append(j)
                    break
            if len(top_pieces) < i+1:
                top_pieces.append(19)
        mean = sum(top_pieces)/len(top_pieces)
        squared_errors = [(top_pieces[i]-mean)**2 for i in range(0, len(top_pieces))]
        return (math.sqrt(sum(squared_errors)/len(top_pieces)), mean)

    def lineclear(self, last_y):
        clear_y = []
        for i in range(last_y, 20):
            count = 0
            for j in range(0, 10):
                if self.board[i][j] == 0:
                    break
                count += 1
            if count == 10:
                clear_y.append(i)
        for i in range(len(clear_y)-1, -1, -1):
            '''for j in range(clear_y[i]-1, -1, -1):
                self.board[j+1] = deepcopy(self.board[j])'''
            #self.board[1:clear_y[i]+1] = deepcopy(self.board[0:clear_y[i]])
            self.board[1:clear_y[i]+1] = ujson.loads(ujson.dumps(self.board[0:clear_y[i]]))
            for l in range(0, len(clear_y)):
                clear_y[l] += 1
                         
        return len(clear_y)
    
    def is_ended(self):
        for i in range(0, 10):
            if self.board[0][i] != 0:
                return True
        return False

class AI:
    def __init__(self, tetrisboard):
        self.mainboard = tetrisboard
    
    def set_mainboard(self, tetrisboard):
        self.mainboard = tetrisboard

    def get_score(self, baseboard, piece, rotation, x, piece2, rotation2, x2):
        board_time = time.time()
        newboard = Tetrisboard()
        newboard.setboard(baseboard.getboard())
        #print("Boardtime", time.time()-board_time)

        piece_time = time.time()
        last_y = newboard.add_piece(piece, x, rotation)
        cleared = newboard.lineclear(last_y)

        last_y = newboard.add_piece(piece2, x2, rotation2)
        cleared = newboard.lineclear(last_y)
        #print("Piecetime", time.time()-piece_time)
        '''
        newboard.drawboard()
        root.update()
        canvas.delete("all")
        '''
        if newboard.is_ended():
            return -9999
        skyline, level = newboard.skyline()
        #print(level)
        score_time = time.time()
        score = (1/(newboard.holecount(last_y)+1)**2)*(1/(skyline+1)**2)*((cleared+1)**0)*((level)/19)**20
        #print("Scoretime", time.time()-score_time)
        return score
    
    def next_move(self, piece_index, second_piece):
        longer_side = min(len(tetris_shapes[piece_index]), len(tetris_shapes[piece_index][0])) # maximum amount of shifting x-axis
        longer_side2 = min(len(tetris_shapes[second_piece]), len(tetris_shapes[second_piece][0]))
        max_rotations = 4
        max_rotations2 = 4
        
        if piece_index == 6:
            max_rotations = 1
        elif piece_index in [1, 2, 5]:
            max_rotations = 2

        if second_piece == 6:
            max_rotations2 = 1
        elif second_piece in [1, 2, 5]:
            max_rotations2 = 2

        best_move = [0, 0, 0]
        highest_score = -99999
            
        for i in range(0, max_rotations):
            for j in range(0, 11-longer_side):
                for l in range(0, max_rotations2):
                    for m in range(0, 11-longer_side2):
                        mid_score = self.get_score(self.mainboard, piece_index, i, j, second_piece, l, m)
                        if mid_score > highest_score:
                            best_move[0] = piece_index
                            best_move[1] = i
                            best_move[2] = j
                            highest_score = mid_score
        return best_move
  

tetris = Tetrisboard()
tetris_AI = AI(tetris)

linescleared = 0

loop = True

pieces = [0,1,2,3,4,5,6]
que = []
add_que = deepcopy(pieces)
random.shuffle(add_que)
que += add_que
add_que = deepcopy(pieces)
random.shuffle(add_que)
que += add_que

start_time = time.time()
printtime = True

while loop:
    pps_time = time.time()
    canvas.delete("all")

    tetris_AI.set_mainboard(tetris)
    
    if len(que) == 7:
        #add_que = deepcopy(pieces)
        add_que = ujson.loads(ujson.dumps(pieces))
        random.shuffle(add_que)
        que += add_que
    next_move = tetris_AI.next_move(que[0], que[1])
    del que[0]

    last_y = tetris.add_piece(next_move[0], next_move[2], next_move[1])

    if tetris.is_ended():
        print(linescleared)
        break
    
    time.sleep(1/pps-(pps_time-time.time()))   # comment out to remove pps limit

    tetris.drawboard()
    #tetris.printboard()
    canvas.create_text(280, 20, text=str(linescleared), font=("Arial", 16), fill="#FFFFFF")
    root.update()

    temp_linescleared = tetris.lineclear(last_y)
    
    if temp_linescleared > 0:
        linescleared += temp_linescleared
        tetris.drawboard()
        canvas.create_text(280, 20, text=str(linescleared), font=("Arial", 16), fill="#FFFFFF")
        #time.sleep(1/fps)
        root.update()
    
    if linescleared >= 40 and printtime:
        print("40 lines in:",time.time()-start_time)
        printtime = False
root.mainloop()
