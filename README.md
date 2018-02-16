I've loaded the MAG data into a database and exported the PaperReferences into a TSV.
Now it's time to run Infomap.

remember to use the virtual environment:
`source venv/bin/activate`
`pip install -r requirements.txt`

+ Convert the TSV to a pajek (.net) file
+ Try to run Infomap
+ If the network is too big, try RelaxMap


2017-12-30
nohup ~/code/RelaxMap/ompRelaxmap 999 ~/code/infomap_mag_snapshot/data/PaperReferences_academicgraphdls_20171110.net 18 1 1e-4 0.0 10 ~/code/infomap_mag_snapshot/data/relaxmap_2 prior >& relaxmap_academicgraphdls_20171230.log &
