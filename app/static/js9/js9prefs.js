var JS9Prefs = {
  "globalOpts": {
		"helperType":	     "nodejs",
		"helperPort":       2718, 
		"helperCGI":        "./cgi-bin/js9/js9Helper.cgi",
		"fits2png":         false,
		"debug":	     0,
		"loadProxy":	     true,
		"workDir":	     "./tmp",
		"workDirQuota":     100,
		"dataPath":	     "$HOME/Desktop:$HOME/data",
		"analysisPlugins":  "./analysis-plugins",
		"analysisWrappers": "./analysis-wrappers",
    "mouseActions": ["display value/position", "pan the image", "change contrast/bias"]
	},
  "imageOpts":  {
		"colormap":	     "grey",
		"scale":     	     "log"
	},
  "emscriptenOpts": { 
		"wasmBinaryFile": "static/js9/astroemw.wasm" 
	}
}
