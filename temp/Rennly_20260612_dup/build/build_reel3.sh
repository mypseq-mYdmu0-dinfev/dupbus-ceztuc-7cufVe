#!/bin/bash
set -e
cd "$(dirname "$0")"
IMG="../resource"
OVD="ov2"
FPS=120
ZINC=0.00017

build_scene() {
  local out="$1" img="$2" D="$3"; shift 3
  local DN=$(echo "$D*$FPS/1" | bc)
  local inputs=(-loop 1 -t "$D" -i "$IMG/$img" -loop 1 -t "$D" -i scrim_bottom.png -loop 1 -t "$D" -i scrim_top.png)
  local fc="[0:v]scale=1350:-2,setsar=1,zoompan=z='min(zoom+${ZINC},1.10)':d=$DN:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=$FPS[bg];[bg][1:v]overlay=0:0[bs];[bs][2:v]overlay=0:0[v0];"
  local idx=3 prev="v0" n=0
  for spec in "$@"; do
    IFS=':' read -r f fin_st fin_d fout_st fout_d <<< "$spec"
    inputs+=(-loop 1 -t "$D" -i "$OVD/$f")
    local fade="format=rgba,fade=t=in:st=${fin_st}:d=${fin_d}:alpha=1"
    if [ -n "$fout_st" ]; then fade="${fade},fade=t=out:st=${fout_st}:d=${fout_d}:alpha=1"; fi
    fc+="[${idx}:v]${fade}[o${n}];[${prev}][o${n}]overlay=0:0[s${n}];"
    prev="s${n}"; idx=$((idx+1)); n=$((n+1))
  done
  fc="${fc%;}"
  ffmpeg -y "${inputs[@]}" -filter_complex "$fc" -map "[${prev}]" -r $FPS -t "$D" \
    -pix_fmt yuv420p -c:v libx264 -crf 18 -preset medium "clips/${out}" -loglevel error
  echo "built clips/${out}"
}

build_scene v2_s1.mp4 render_exterior_dusk.png 5.2 "s1_hook.png:0.2:0.4:2.4:0.4" "s1_brand.png:2.8:0.6::"
build_scene v2_s2.mp4 render_living.png        5.2 "s2.png:0.4:0.6:4.8:0.4"
build_scene v2_s3.mp4 render_kitchen.png       5.0 "s3.png:0.4:0.6:4.6:0.4"
build_scene v2_s4.mp4 render_bedroom.png       5.0 "s4.png:0.4:0.6:4.6:0.4"
build_scene v2_s5.mp4 render_amenity1.png      5.6 "s5.png:0.4:0.6:5.2:0.4"
build_scene v2_s6.mp4 render_aerial.png        7.0 "s6_brand.png:0.3:0.6::" "s6_specs.png:0.5:0.6:3.4:0.5" "s6_cta.png:4.0:0.6::"

echo "concatenating (120fps crossfades)..."
ffmpeg -y -i clips/v2_s1.mp4 -i clips/v2_s2.mp4 -i clips/v2_s3.mp4 -i clips/v2_s4.mp4 -i clips/v2_s5.mp4 -i clips/v2_s6.mp4 \
 -filter_complex "[0][1]xfade=transition=fade:duration=0.6:offset=4.6[a];[a][2]xfade=transition=fade:duration=0.6:offset=9.2[b];[b][3]xfade=transition=fade:duration=0.6:offset=13.6[c];[c][4]xfade=transition=fade:duration=0.6:offset=18.0[d];[d][5]xfade=transition=fade:duration=0.6:offset=23.0[v]" \
 -map "[v]" -r $FPS -pix_fmt yuv420p -c:v libx264 -crf 19 -preset medium -movflags +faststart clips/v2_silent.mp4 -loglevel error

# add silent audio track
ffmpeg -y -i clips/v2_silent.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
 -c:v copy -c:a aac -shortest -movflags +faststart "../AUREA_Rhodes_Reel_v2.mp4" -loglevel error
echo "DONE v2"
ffprobe -v error -of default=nw=1 -show_entries format=duration,size:stream=codec_type,width,height,r_frame_rate "../AUREA_Rhodes_Reel_v2.mp4"
