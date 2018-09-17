function parameterValues = operatorParameters(th)

[thS0m, thF0m, thF0a, thS0a] = deal(60, 43, 83, 69);
Ei = 50;        Eiii = 80;         sS0m = 110;

cm = 10.6;      ca = 10.6;
ein = 24;

[sSxm, sFxm] = deal(max(sS0m, cm*(th - thS0m)),  max(460, cm*(th - thF0m)));
[eSxm, eFxm] = deal(sSxm/Ei,  (sFxm/Eiii) + ein);
[sSxa,  sFxa] = deal(ca*(th - thS0a),    ca*(th - thF0a));
[eFxa, eSxa] = deal(sFxa/Ei, (sSxa/Eiii)+ein);
Eii = (sFxm - sSxm)/(eFxm - eSxm);
Eiv = (sFxa - sSxa)/(eFxa - eSxa);

Es = {Ei, Eii, Eiii, Eiv, ein};   ses = {sSxm, sFxm, sSxa,  sFxa};    ees = {eSxm, eFxm, eSxa,  eFxa};
parameterValues = {Es, ses, ees};