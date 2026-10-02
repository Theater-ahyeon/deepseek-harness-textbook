"""Draw original technical diagrams as SVG and PNG, using Chinese labels."""
import json
import math
import textwrap
from html import escape
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
DATA = json.loads((OUT / "figure-data.json").read_text(encoding="utf-8"))
FONT = Path("C:/Windows/Fonts/msyh.ttc")
BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
PALETTE = {"user":("#E9F2FF","#3469A8"),"control":("#F0EBFF","#7659AA"),"model":("#FFF2CC","#A97F16"),"tool":("#E5F6ED","#367E5A"),"log":("#EDF1F5","#63758A"),"error":("#FFE8E5","#BB5348")}
FLOW_LABELS = {
    "F01A":["组织请求","调用提议","完成读取","交付材料","生成回答"],
    "F04A":["提交参数","获准分派","取得文本","按契约渲染","记录结果"],
    "F07A":["摘要整理","查找名称","验证许可","交付正文","再入请求"],
    "F09A":["发起请求","发布片段","终结检查","提交事实","仅成功继续"],
    "F10A":["依次应用","继续覆盖","继续覆盖","完成组合","挂载贡献"],
    "F11A":["准备调用","需要时询问","允许才进入","执行后处理","形成结果"],
    "F12A":["能力协商","构建定义","交换注册","请求调用","分派远端"],
    "F14B":["建立游标","消费缓冲","验证序号","合并事实","通知视图"],
    "F15B":["加载资源","等待资料","后端启动","就绪交接","同文档继续"],
    "F16A":["还原响应","注册边界","驱动执行","观察事实","检查消费"],
    "F18A":["选择接口","满足依赖","提出调用","结果提交","结束生命周期"],
    "F20A":["检查事实","归因定位","确定落点","验证生效","评价结果"]
}


class Canvas:
    def __init__(self, data):
        self.data = data
        self.image = Image.new("RGB",(1120,760),"white")
        self.draw = ImageDraw.Draw(self.image)
        figure_id = data["id"]
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="760" viewBox="0 0 1120 760" role="img" aria-labelledby="{figure_id}-title {figure_id}-desc">', f'<title id="{figure_id}-title">{escape(data["id"]+"："+data["title"])}</title>',f'<desc id="{figure_id}-desc">{escape(json.dumps(data,ensure_ascii=False))}</desc>','<rect width="1120" height="760" fill="white"/>']

    def text(self,x,y,text,size=20,bold=False,color="#20314B",max_width=None):
        font = ImageFont.truetype(str(BOLD if bold else FONT),size)
        paragraphs = str(text).split("\n")
        output=[]
        for p in paragraphs:
            current=""
            for char in p:
                if max_width and current and self.draw.textlength(current+char,font=font)>max_width:
                    output.append(current)
                    current=char
                else:
                    current+=char
            output.append(current)
        for i,line in enumerate(output):
            ty=y+i*(size+10)
            self.draw.text((x,ty),line,font=font,fill=color,stroke_width=0)
            self.svg.append(f'<text x="{x}" y="{ty+size}" font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(line)}</text>')
        return len(output)*(size+10)

    def rect(self,x,y,w,h,kind="log",fill=None,stroke=None):
        colors=PALETTE[kind]
        fill,stroke=fill or colors[0],stroke or colors[1]
        self.draw.rounded_rectangle((x,y,x+w,y+h),radius=16,fill=fill,outline=stroke,width=2)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

    def arrow(self,points,color="#65738A",label=None,at=None):
        self.draw.line(points,fill=color,width=3,joint="curve")
        (ax,ay),(bx,by)=points[-2:]
        theta=math.atan2(by-ay,bx-ax)
        head=[(bx,by),(bx-11*math.cos(theta-0.5),by-11*math.sin(theta-0.5)),(bx-11*math.cos(theta+0.5),by-11*math.sin(theta+0.5))]
        self.draw.polygon(head,fill=color)
        joined=" ".join(f"{x},{y}" for x,y in points)
        tip=" ".join(f"{x:.1f},{y:.1f}" for x,y in head)
        self.svg.extend([f'<polyline points="{joined}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>',f'<polygon points="{tip}" fill="{color}"/>'])
        if label and at:
            self.text(*at,label,15,color=color,max_width=140)

    def header(self):
        self.text(48,28,self.data["id"]+"  "+self.data["title"],28,True,max_width=1030)
        self.text(48,80,"原创教学图 · "+self.data["tag"],17,color="#65738A")

    def card(self,x,y,w,h,lines,kind="log"):
        self.rect(x,y,w,h,kind)
        pos=y+24
        pos+=self.text(x+22,pos,lines[0],23,True,max_width=w-44)+18
        for line in lines[1:]:
            pos+=self.text(x+22,pos,line,20,max_width=w-44)+19
        if pos>y+h+5:
            raise ValueError(f"Card overflow: {self.data['id']}, {lines}")

    def finish(self):
        self.text(48,710,"读图：先确认范围，再跟随标注；示意布局不代表实际耗时或比例。",16,color="#65738A",max_width=1024)
        self.svg.append("</svg>")
        (OUT/(self.data["id"]+".svg")).write_text("\n".join(self.svg),encoding="utf-8")
        self.image.save(OUT/(self.data["id"]+".png"),optimize=True)


for d in DATA:
    c=Canvas(d)
    c.header()
    kind=d["kind"]
    if kind=="flow":
        positions=[(55,140),(405,140),(755,140),(755,410),(405,410),(55,410)]
        for i,(title,detail,cat) in enumerate(d["nodes"]):
            x,y=positions[i]
            c.card(x,y,310,165,[f"{i+1}  {title}",detail],cat)
        labels=FLOW_LABELS[d["id"]]
        for i in range(5):
            x,y=positions[i]; nx,ny=positions[i+1]
            if y==ny:
                if nx>x: points=[(x+310,y+100),(nx,y+100)]; at=(x+309,y+40)
                else: points=[(x,y+100),(nx+310,ny+100)]; at=(nx+305,y+40)
                # Space is narrow: place the label below its connector, allowing a short wrap.
                c.arrow(points)
                center=(points[0][0]+points[1][0])/2
                c.text(center-42,y+175,labels[i],15,max_width=110)
            else:
                c.arrow([(x+155,y+165),(nx+155,ny)],label=labels[i],at=(x+171,y+197))
        if d["id"]=="F11A":
            c.arrow([(1065,230),(1095,230),(1095,655),(560,655),(560,575)],color="#BB5348",label="拒绝：跳过执行体",at=(790,623))
    elif kind=="compare":
        c.card(48,150,495,470,d["left"],"control")
        c.card(577,150,495,470,d["right"],"tool")
    elif kind=="columns":
        for i,column in enumerate(d["columns"]):
            c.card(55+i*350,150,310,470,column,["user","control","tool"][i])
    elif kind=="fan":
        c.card(340,125,440,140,d["origin"],"log")
        # Compact two-line origin uses a smaller custom height requirement.
        for i,column in enumerate(d["columns"]):
            x=55+i*350
            c.card(x,340,310,290,column,["model","control","tool"][i])
            points=[(560,265),(560,300),(x+155,300),(x+155,340)]
            if d.get("reverse"):
                points=points[::-1]
            c.arrow(points)
        c.text(48,265,"材料汇合" if d.get("reverse") else "按用途消费",17,color="#65738A")
    elif kind=="nested":
        c.rect(48,135,1024,505,"control")
        c.text(75,158,d["outer"],25,True)
        for i,items in enumerate(d["inner"]):
            c.card(75+i*495,220,465,280,items,"model")
        c.text(75,552,d["note"],21,True,max_width=970)
    else:
        raise ValueError(kind)
    c.finish()
print(f"Generated {len(DATA)} original SVG + PNG figures")
