#!/bin/bash

rm /caa/web/flask/plot_panels-stage/xml/CAA_PANEL_*.XML
cp ~dherment/FlaskApp/xml/CAA_PANEL_*.XML /caa/web/flask/plot_panels-stage/xml

mv /caa/web/flask/plot_panels-stage/xml/*FGM_SPIN* /caa/web/flask/plot_panels-stage/xml/fgm
mv /caa/web/flask/plot_panels-stage/xml/*FGM_FULL* /caa/web/flask/plot_panels-stage/xml/fgm
mv /caa/web/flask/plot_panels-stage/xml/*FGM_5VPS* /caa/web/flask/plot_panels-stage/xml/fgm

rm /caa/web/flask/plot_panels-stage/xml/CAA_PANEL_C2_CG_MULT_CIS_RAP_PROTON_OMNI_CAA.XML 

