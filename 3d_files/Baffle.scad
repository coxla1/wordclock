sz = 200; // Total size
h = 6; // Height
n = 12; // Number of boxes
sep = 1; // Size of each separator
boxsz = (sz-(n+1)*sep)/n; // Size of each box
wireh = 2; // Wire height
wiresz = 3/5*boxsz; // Size of each wire space
wiresep = (sz-sep)/n-wiresz; // Size of each wire separator

module line(x,y,h,sepx,n) {
    for (i = [1:n]) {
        translate([(i-1)*x + i*sepx,0,0])
            cube([x,y,h]);
    }
}

module grid(x,y,h,sepx,sepy,n) {
    for (j = [1:n]) {
        translate([0,(j-1)*y + j*sepy,0])
            line(x,y,h,sepx,n);
    }
}

difference() {
    cube([sz,sz,h]);
    grid(boxsz,boxsz,h,sep,sep,n);
    translate([-(wiresep-sep)/2,0,h-wireh])
        line(wiresz,sep,wireh,wiresep,n);
    translate([-(wiresep-sep)/2,sz-sep,h-wireh])
        line(wiresz,sep,wireh,wiresep,n);
}


