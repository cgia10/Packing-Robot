import matplotlib.pyplot as plt
import numpy as np
import glob
import os
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image


def gifGenerator(filenames):
    frames = []
    for i in filenames:
        new_frame = Image.open(i)
        frames.append(new_frame)
    
    frames[0].save('visualization/gif.gif', format='GIF',
                append_images=frames[1:],
                save_all=True,
                duration=1000)
    print('visualization/gif.gif saved')


def visualize(seq, container_size, x_pos, y_pos, z_pos, a_len, b_len, c_len, shrink_ratio=5):

    # shrink
    shrink = lambda li: list(map(lambda length: int(length/shrink_ratio), li))
    container_size = shrink(container_size)
    x_pos, y_pos, z_pos = shrink(x_pos), shrink(y_pos), shrink(z_pos)
    a_len, b_len, c_len = shrink(a_len), shrink(b_len), shrink(c_len)

    # empty the folder
    files = glob.glob('visualization/*')
    for f in files:
        os.remove(f)

    # draw figures
    color_packed = 'orange'
    filenames = []
    # x_points, y_points, z_points = [], [], []
    filled = np.zeros(tuple(container_size), dtype=bool)
    colors = np.empty(filled.shape, dtype=object)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlabel('x (%dmm)'%shrink_ratio)
    ax.set_ylabel('y (%dmm)'%shrink_ratio)
    ax.set_zlabel('z (%dmm)'%shrink_ratio)
    ax.set_xlim3d(0.0, container_size[0])
    ax.set_ylim3d(0.0, container_size[1])
    ax.set_zlim3d(0.0, container_size[2])
    ax.set_xticks(range(0, container_size[0]+1, 5))
    ax.set_yticks(range(0, container_size[1]+1, 5))
    ax.set_zticks(range(0, container_size[2]+1, 5))
    ax.view_init(30, 110)
    ax.voxels(filled, facecolors=colors, alpha=0.9)
    
    filenames.append('visualization/0.png')
    plt.title(' ')
    plt.savefig(filenames[-1])
    print(filenames[-1], 'saved')

    for i in range(len(seq)):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.set_xlabel('x (%dmm)'%shrink_ratio)
        ax.set_ylabel('y (%dmm)'%shrink_ratio)
        ax.set_zlabel('z (%dmm)'%shrink_ratio)
        ax.set_xlim3d(0.0, container_size[0])
        ax.set_ylim3d(0.0, container_size[1])
        ax.set_zlim3d(0.0, container_size[2])
        ax.set_xticks(range(0, container_size[0]+1, 5))
        ax.set_yticks(range(0, container_size[1]+1, 5))
        ax.set_zticks(range(0, container_size[2]+1, 5))
        ax.view_init(30, 110)
        filled[x_pos[seq[i]]:x_pos[seq[i]] + a_len[seq[i]], y_pos[seq[i]]:y_pos[seq[i]] + b_len[seq[i]], z_pos[seq[i]]:z_pos[seq[i]] + c_len[seq[i]]] = True
        colors[x_pos[seq[i]]:x_pos[seq[i]] + a_len[seq[i]], y_pos[seq[i]]:y_pos[seq[i]] + b_len[seq[i]], z_pos[seq[i]]:z_pos[seq[i]] + c_len[seq[i]]] = color_packed # color_new
        ax.voxels(filled, facecolors=colors, alpha=0.9)
        
        filenames.append('visualization/%d.png'%(i+1))
        plt.title('Item #%d Packed'%seq[i])
        plt.savefig(filenames[-1])
        print(filenames[-1], 'saved')

    gifGenerator(filenames)


if __name__ == "__main__":

    container_size = [150, 95, 80]
    x_pos = [95, 50, 0, 85, 35, 0]
    y_pos = [0, 40, 55, 55, 0, 0]
    z_pos = [0, 0, 0, 0, 0, 0]
    a_len = [55, 35, 50, 65, 55, 35]
    b_len = [55, 55, 35, 35, 40, 45]
    c_len = [55, 50, 65, 55, 60, 35]
    seq = range(len(x_pos))

    imgs = visualize(seq, container_size, x_pos, y_pos, z_pos, a_len, b_len, c_len, shrink_ratio=5)