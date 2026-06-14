#!/bin/bash
set -e
cd "$(dirname "$0")"

IMG=".."
SERIF="/System/Library/Fonts/Supplemental/Didot.ttc"
FUT="/System/Library/Fonts/Supplemental/Futura.ttc"
AVE="/System/Library/Fonts/Avenir Next.ttc"
CJK="/System/Library/Fonts/STHeiti Medium.ttc"

CREAM="0xF5EFE6"
WHITE="0xFFFFFF"
AMBER="0xE8A23D"
DARK="0x1A1410"
SH="shadowcolor=black@0.55:shadowx=2:shadowy=3"

# common zoompan + scrims, produces [sc]
base() { # $1 img  $2 DN
  echo "[0:v]scale=1350:-2,setsar=1,zoompan=z='min(zoom+0.0006,1.10)':d=$2:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30[bg];[bg][1:v]overlay=0:0[bs];[bs][2:v]overlay=0:0[sc];"
}

mk() { # $1 imgfile $2 D $3 filtertail(after [sc]) -> outfile $4
  local DN=$(echo "$2*30/1" | bc)
  ffmpeg -y -loop 1 -t "$2" -i "$IMG/$1" -i scrim_bottom.png -i scrim_top.png \
    -filter_complex "$(base "$1" "$DN")[sc]$3[v]" \
    -map "[v]" -r 30 -t "$2" -pix_fmt yuv420p -c:v libx264 -crf 18 -preset medium "clips/$4" -loglevel error
  echo "built clips/$4"
}

# ---------- Scene 1: HOOK (exterior) D=4.6 ----------
S1="drawtext=fontfile=$FUT:textfile=txt/t1a.txt:fontcolor=$WHITE:fontsize=86:x=(w-tw)/2:y=h*0.40:$SH:alpha='if(lt(t,0.2),0,if(lt(t,0.6),(t-0.2)/0.4,if(lt(t,1.8),1,if(lt(t,2.2),(2.2-t)/0.4,0))))',\
drawtext=fontfile=$SERIF:textfile=txt/t1_brand.txt:fontcolor=$CREAM:fontsize=176:x=(w-tw)/2:y=h*0.34:$SH:alpha='if(lt(t,2.2),0,if(lt(t,2.8),(t-2.2)/0.6,1))',\
drawbox=x=(iw-240)/2:y=h*0.34+250:w=240:h=3:color=$AMBER@0.95:t=fill:enable='gt(t,2.95)',\
drawtext=fontfile=$FUT:textfile=txt/t1_kick.txt:fontcolor=$AMBER:fontsize=33:x=(w-tw)/2:y=h*0.34+285:$SH:alpha='if(lt(t,3.0),0,if(lt(t,3.5),(t-3.0)/0.5,1))'"
mk render_exterior_dusk.png 4.6 "$S1" s1.mp4

# ---------- Scene 2: living D=4.6 ----------
LT2="drawtext=fontfile=$SERIF:textfile=txt/t2a.txt:fontcolor=$CREAM:fontsize=66:x=(w-tw)/2:y=h*0.70:$SH:alpha='if(lt(t,0.4),0,if(lt(t,1.0),(t-0.4)/0.6,if(lt(t,4.2),1,(4.6-t)/0.4)))',\
drawtext=fontfile=$AVE:textfile=txt/t2b.txt:fontcolor=$WHITE@0.92:fontsize=38:x=(w-tw)/2:y=h*0.70+95:$SH:alpha='if(lt(t,0.9),0,if(lt(t,1.5),(t-0.9)/0.6,if(lt(t,4.2),1,(4.6-t)/0.4)))',\
drawtext=fontfile=$SERIF:textfile=txt/brand.txt:fontcolor=$CREAM@0.85:fontsize=44:x=70:y=h-120:$SH:alpha='if(lt(t,0.6),0,if(lt(t,1.2),(t-0.6)/0.6,1))'"
mk render_living.png 4.6 "$LT2" s2.mp4

# ---------- Scene 3: kitchen D=4.2 ----------
LT3="drawtext=fontfile=$SERIF:textfile=txt/t3a.txt:fontcolor=$CREAM:fontsize=66:x=(w-tw)/2:y=h*0.70:$SH:alpha='if(lt(t,0.4),0,if(lt(t,1.0),(t-0.4)/0.6,if(lt(t,3.8),1,(4.2-t)/0.4)))',\
drawtext=fontfile=$AVE:textfile=txt/t3b.txt:fontcolor=$WHITE@0.92:fontsize=38:x=(w-tw)/2:y=h*0.70+95:$SH:alpha='if(lt(t,0.9),0,if(lt(t,1.5),(t-0.9)/0.6,if(lt(t,3.8),1,(4.2-t)/0.4)))',\
drawtext=fontfile=$SERIF:textfile=txt/brand.txt:fontcolor=$CREAM@0.85:fontsize=44:x=70:y=h-120:$SH:alpha='if(lt(t,0.6),0,if(lt(t,1.2),(t-0.6)/0.6,1))'"
mk render_kitchen.png 4.2 "$LT3" s3.mp4

# ---------- Scene 4: bedroom D=4.2 ----------
LT4="drawtext=fontfile=$SERIF:textfile=txt/t4a.txt:fontcolor=$CREAM:fontsize=72:x=(w-tw)/2:y=h*0.71:$SH:alpha='if(lt(t,0.4),0,if(lt(t,1.0),(t-0.4)/0.6,if(lt(t,3.8),1,(4.2-t)/0.4)))',\
drawtext=fontfile=$SERIF:textfile=txt/brand.txt:fontcolor=$CREAM@0.85:fontsize=44:x=70:y=h-120:$SH:alpha='if(lt(t,0.6),0,if(lt(t,1.2),(t-0.6)/0.6,1))'"
mk render_bedroom.png 4.2 "$LT4" s4.mp4

# ---------- Scene 5: amenity D=4.8 ----------
LT5="drawtext=fontfile=$SERIF:textfile=txt/t5a.txt:fontcolor=$CREAM:fontsize=66:x=(w-tw)/2:y=h*0.70:$SH:alpha='if(lt(t,0.4),0,if(lt(t,1.0),(t-0.4)/0.6,if(lt(t,4.4),1,(4.8-t)/0.4)))',\
drawtext=fontfile=$AVE:textfile=txt/t5b.txt:fontcolor=$AMBER:fontsize=38:x=(w-tw)/2:y=h*0.70+95:$SH:alpha='if(lt(t,0.9),0,if(lt(t,1.5),(t-0.9)/0.6,if(lt(t,4.4),1,(4.8-t)/0.4)))',\
drawtext=fontfile=$SERIF:textfile=txt/brand.txt:fontcolor=$CREAM@0.85:fontsize=44:x=70:y=h-120:$SH:alpha='if(lt(t,0.6),0,if(lt(t,1.2),(t-0.6)/0.6,1))'"
mk render_amenity1.png 4.8 "$LT5" s5.mp4

# ---------- Scene 6: aerial + specs + CTA D=6.8 ----------
S6="drawtext=fontfile=$SERIF:textfile=txt/brand.txt:fontcolor=$CREAM:fontsize=70:x=(w-tw)/2:y=140:$SH:alpha='if(lt(t,0.3),0,if(lt(t,0.9),(t-0.3)/0.6,1))',\
drawtext=fontfile=$FUT:textfile=txt/t6s1.txt:fontcolor=$CREAM:fontsize=42:x=(w-tw)/2:y=h*0.30:$SH:alpha='if(lt(t,0.4),0,if(lt(t,1.0),(t-0.4)/0.6,if(lt(t,3.0),1,(3.5-t)/0.5)))',\
drawtext=fontfile=$FUT:textfile=txt/t6s2.txt:fontcolor=$AMBER:fontsize=46:x=(w-tw)/2:y=h*0.30+72:$SH:alpha='if(lt(t,0.6),0,if(lt(t,1.2),(t-0.6)/0.6,if(lt(t,3.0),1,(3.5-t)/0.5)))',\
drawtext=fontfile=$FUT:textfile=txt/t6s3.txt:fontcolor=$CREAM:fontsize=42:x=(w-tw)/2:y=h*0.30+148:$SH:alpha='if(lt(t,0.8),0,if(lt(t,1.4),(t-0.8)/0.6,if(lt(t,3.0),1,(3.5-t)/0.5)))',\
drawbox=x=(iw-620)/2:y=h*0.60:w=620:h=112:color=$AMBER@0.96:t=fill:enable='gt(t,3.7)',\
drawtext=fontfile=$FUT:textfile=txt/t6c1.txt:fontcolor=$DARK:fontsize=46:x=(w-tw)/2:y=h*0.60+34:alpha='if(lt(t,3.7),0,if(lt(t,4.2),(t-3.7)/0.5,1))',\
drawtext=fontfile=$AVE:textfile=txt/t6c2.txt:fontcolor=$CREAM:fontsize=42:x=(w-tw)/2:y=h*0.60+150:$SH:alpha='if(lt(t,4.0),0,if(lt(t,4.5),(t-4.0)/0.5,1))',\
drawtext=fontfile=$CJK:textfile=txt/t6cn.txt:fontcolor=$AMBER:fontsize=46:x=(w-tw)/2:y=h*0.74:$SH:alpha='if(lt(t,4.4),0,if(lt(t,5.0),(t-4.4)/0.6,1))'"
mk render_aerial.png 6.8 "$S6" s6.mp4

# ---------- xfade concatenate ----------
echo "concatenating with crossfades..."
ffmpeg -y -i clips/s1.mp4 -i clips/s2.mp4 -i clips/s3.mp4 -i clips/s4.mp4 -i clips/s5.mp4 -i clips/s6.mp4 \
 -filter_complex "\
[0][1]xfade=transition=fade:duration=0.6:offset=4.0[a]; \
[a][2]xfade=transition=fade:duration=0.6:offset=8.0[b]; \
[b][3]xfade=transition=fade:duration=0.6:offset=11.6[c]; \
[c][4]xfade=transition=fade:duration=0.6:offset=15.2[d]; \
[d][5]xfade=transition=fade:duration=0.6:offset=19.4[v]" \
 -map "[v]" -r 30 -pix_fmt yuv420p -c:v libx264 -crf 19 -preset slow -movflags +faststart \
 "../AUREA_Rhodes_Reel.mp4" -loglevel error
echo "DONE: ../AUREA_Rhodes_Reel.mp4"
