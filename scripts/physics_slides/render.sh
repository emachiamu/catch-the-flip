SP=$(cd "$(dirname "$0")" && pwd); D=~/Library/Containers/com.microsoft.Powerpoint/Data; DECK=/Users/trinity/catch-the-flip/catch_the_flip_physics.pptx
$SP/venv/bin/python -I $SP/plots.py $SP/out > /dev/null 2>&1 || { echo plots failed; exit 1; }
NODE_PATH=$SP/node_modules node $SP/build.js $SP/out $DECK || exit 1
SK="/Users/trinity/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/b17751b2-b157-416e-ab13-a2265283385d/e9aa77cc-011a-44af-b1a6-c7df1ae623cb/skills/pptx"
$SP/venv/bin/python "$SK/scripts/office/validate.py" $DECK
cp $DECK $D/tmp_phys.pptx
osascript -e "tell application \"Microsoft PowerPoint\"
open POSIX file \"$D/tmp_phys.pptx\"
delay 4
save active presentation in POSIX file \"$D/tmp_phys.pdf\" as save as PDF
close active presentation saving no
end tell"
mv $D/tmp_phys.pdf $SP/phys.pdf; rm -f $D/tmp_phys.pptx $SP/p-*.png
$SP/venv/bin/python -I -W ignore -c "
import pymupdf
for i,p in enumerate(pymupdf.open('$SP/phys.pdf')): p.get_pixmap(dpi=80).save(f'$SP/p-{i+1:02d}.png')
print('pages', i+1)"
