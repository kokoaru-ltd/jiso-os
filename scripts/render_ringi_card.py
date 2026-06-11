#!/usr/bin/env python3
"""OSが自分のDB実データから投稿用の稟議カード画像を描画する（スクショの自給自足）"""
from PIL import Image, ImageDraw, ImageFont
import sys, json

def render(data, out, lang="ja"):
    W,H = 1600,900
    img = Image.new("RGB",(W,H),"#101724")
    d = ImageDraw.Draw(img)
    # 背景: 夜の藍グラデ + 金のシャフト
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)],fill=(int(16+8*t),int(23+6*t),int(36+4*t)))
    for x in range(int(W*0.62),int(W*0.78)):
        a=1-abs(x-W*0.70)/(W*0.08)
        if a>0:
            for y in range(H):
                px=img.getpixel((x,y)); g=int(40*a)
                img.putpixel((x,y),(min(255,px[0]+g),min(255,px[1]+int(g*0.8)),min(255,px[2]+int(g*0.35))))
    d = ImageDraw.Draw(img)
    F = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    f_label=ImageFont.truetype(F,26); f_title=ImageFont.truetype(FB,52)
    f_kv=ImageFont.truetype(F,34); f_kvb=ImageFont.truetype(FB,40); f_small=ImageFont.truetype(F,24)
    gold="#e8c184"; white="#eef2f6"; dim="#8b99ab"; shu="#ff5a44"
    # カード
    cx,cy,cw,ch = 110,120,1020,660
    d.rounded_rectangle([cx,cy,cx+cw,cy+ch],18,fill="#161e2e",outline="#2a3650",width=2)
    d.text((cx+50,cy+44),f"APPROVAL REQUEST  AR-{data['id']}",font=f_label,fill=gold)
    d.text((cx+cw-60,cy+44),data['filed_at'],font=f_label,fill=dim,anchor="ra")
    d.line([cx+50,cy+100,cx+cw-50,cy+100],fill="#2a3650",width=2)
    # タイトル（折返し）
    title=data['title']; lines=[]; cur=""
    for chs in title:
        cur+=chs
        if d.textlength(cur,font=f_title)>cw-120: lines.append(cur[:-1]); cur=chs
    lines.append(cur)
    ty=cy+130
    for ln in lines[:2]:
        d.text((cx+50,ty),ln,font=f_title,fill=white); ty+=70
    d.text((cx+50,ty+6),f"Filed by: {data['filed_by']}  /  status: {data['status'].upper()}",font=f_small,fill=dim)
    rows=[("Amount", f"¥{data['amount_yen']:,}"),
          ("Projected ROI", f"{data['expected_roi_pct']}%"),
          ("Kill condition", data['exit_condition'])]
    ry=ty+70
    for k,v in rows:
        d.text((cx+50,ry),k,font=f_kv,fill=dim)
        col = shu if "ROI" in k else white
        vf = f_kvb if "ROI" in k or "Amount" in k else f_kv
        # value wrap
        if d.textlength(v,font=vf)>cw-420:
            v=v[:38]+"…"
        d.text((cx+400,ry),v,font=vf,fill=col)
        ry+=86
    d.text((cx+50,cy+ch-66),"⏸ Nothing is spent until a human approves.",font=f_small,fill=gold)
    # 右側ブランド
    d.text((W-90,H-90),"INCAGENT — THE SELF-DRIVING COMPANY",font=f_small,fill=dim,anchor="ra")
    # 判子
    sx,sy,r = 1300,250,95
    d.ellipse([sx-r,sy-r,sx+r,sy+r],outline=shu,width=6)
    f_stamp=ImageFont.truetype(FB,58)
    d.text((sx,sy-16),"承認",font=f_stamp,fill=shu,anchor="mm")
    d.text((sx,sy+42),"PENDING",font=ImageFont.truetype(F,22),fill=shu,anchor="mm")
    img.save(out)
    print("saved:",out)

if __name__=="__main__":
    data=json.loads(sys.argv[1]); render(data,sys.argv[2])
