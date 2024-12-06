# whoseline
Tool for synthesizing dialogues from script

Provide api-key for OpenAI gpt-4o-audio-preview or change to use Azure hosted model.

For converting a script written for instance as alternating cells in a Word table to expected json structure, use ChatGPT with a simple prompt as such:

"Jeg skal angi en dialog mellom en lege og en pasient fra en tabell i word. Jeg vil at du formatterer dialogen på følgende måte: {"actor": 4, "line": "Hei, takk for sist"},
    {"actor": 5, "line": "Takk for sist, ja."},
    {"actor": 4, "line": "Ja, i dag er det cøliakikontroll"},
    {"actor": 5, "line": "Ja.."},
    {"actor": 4, "line": "Så, hvordan går det?"},
    {"actor": 5, "line": "Jo, jeg synes det går greit. Det har vært litt mye å sette seg inn i, men det har blitt lettere etter hvert."} Lege	Pasient
Hei, takk for sist	
	Takk for sist, ja.
Ja, i dag er det cøliakikontroll	
	Ja,
Så hvordan går det?	
	Jo, jeg synes det går greit. Det har vært litt mye å sette seg inn i, men det har blitt lettere etter hvert.
Blodprøvene ser jo også bra ut. Jeg ser på cøliakiprøven, transglutaminase, at du har begynt med glutenfri kost. Verdien har gått fra over 250 til 43 nå. 	
	Åja, hva er vanlig.
 ..."
