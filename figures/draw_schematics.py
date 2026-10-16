"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)


def obstruction(out):
    d=Drawing((-.7,-1.8,12.0,3.4))
    for j,off in enumerate((0,6.0)):
        for tag,x in [('a',off),('b',off+3.0)]:
            for i,y in enumerate((0,1.6)):
                d.box(tag+str(i)+str(j),x,y,.65,.65,'$'+tag+'_'+str(i)+'$',shape='circle')
            d.ax.add_patch(Rectangle((x-.5,-.5),1.0,2.6,fill=False,lw=.55))
            d.text(x,2.55,tag.upper())
    d.edge('a10','b00','e','w')
    d.edge('b10','a00','e','s',via=((4.,1.6),(4.,-.75),(0,-.75)))
    d.edge('a01','b11','e','w')
    d.edge('b01','a11','e','w',via=((10.,0),(10.,3.0),(5.15,3.0),(5.15,1.6)))
    d.text(1.5,-1.1,r'$w_{AB}=w_{BA}=2$')
    d.text(7.5,-1.1,r'$w_{AB}=w_{BA}=0$')
    d.text(1.5,-1.6,'(a) No feasible offsets')
    d.text(7.5,-1.6,r'(b) $o_A=o_B=0$ is valid')
    d.save(out,'obstruction')


def exchange(out):
    d=Drawing((-.8,-1.25,11.4,3.6))
    for tag,y in [('a',2.0),('b',0)]:
        root='x' if tag=='a' else 'y'
        for name,x,label in [(root,0,'$'+root+'$'),(tag+'1',2.2,'$'+tag+'_1$'),(tag+'n',7.2,'$'+tag+'_n$')]:
            d.box(name,x,y,.65,.65,label,shape='circle')
        d.text(4.7,y,r'$\cdots$')
        d.arrow((2.525,y),(4.25,y)); d.arrow((5.15,y),(6.875,y))
        d.ax.add_patch(Rectangle((-.55,y-.55),8.3,1.1,fill=False,lw=.55))
    d.edge('x','a1','e','w',dashed=True)
    d.ax.patches[-1].set_linestyle((0,(1,2)))
    d.edge('y','b1','e','w')
    d.edge('bn','a1','e','n',via=((8.0,0),(8.0,3.0),(2.2,3.0)))
    d.edge('an','b1','s','n',dashed=True,via=((6.5,1.0),(2.2,1.0)))
    d.line([(-.25,2.25),(.25,1.75)])
    d.text(9.6,2.0,r'$o_A:0\to n$')
    d.text(9.6,0,r'$o_B=0$')
    d.text(4.6,-.95,r'Local labels: root $0$, chain position $i$')
    d.save(out,'exchange')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    obstruction(a.output);exchange(a.output)



