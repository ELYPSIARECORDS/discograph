!function(){
    var dg = {};

    dg.color = {
        heatmap: function(d) {
            var hue = ((d.distance / 12) * 360) % 360;
            var variation_a = ((d.id % 5) - 2) / 20;
            var variation_b = ((d.id % 9) - 4) / 80;
            var saturation = 0.67 + variation_a;
            var lightness = 0.5 + variation_b;
            return d3.hsl(hue, saturation, lightness).toString();
        },
    }

    dg.graph = {
        APIURL: "/api/artist/network/",
        cache: d3.map(),
        cacheHistory: [],
        centerNodeID: null,
        dimensions: [0, 0],
        isUpdating: false,
        json: null,
        linkMap: d3.map(),
        links: [],
        newNodeCoords: [0, 0],
        nodeMap: d3.map(),
        nodes: [],
        selectedNodeID: null,
        // selections
        svgSelection: null,
        haloSelection: null,
        nodeSelection: null,
        linkSelection: null,
        textSelection: null,
        // layers
        haloLayer: null,
        textLayer: null,
        nodeLayer: null,
        linkLayer: null,
    };

    dg.history = {
        onPopState: function(event) {
            console.log(event, event.state);
            dg.updateGraph(event.state.id);
        },
        pushState: function(id) {
            var title = document.title;
            var url = "/artist/" + id + "/";
            window.history.pushState({id: id}, title, url);
        },
    }

    /* GRAPH METHODS */

    dg.handleNewGraphData = function(error, json) {
        if (error) return console.warn(error);
        var id = json.center[0];
        if (!dg.graph.cache.has(id)) {
            dg.graph.cache.set(id, JSON.parse(JSON.stringify(json)));
            dg.graph.cacheHistory.push(id);
            if (50 <= dg.graph.cache.size()) {
                dg.graph.cache.remove(dg.graph.cacheHistory.shift());
            }
        }
        var name = json.nodes.filter(function(d) {
            return d.id == id;
        })[0].name;
        $(document).attr("body").id = id;
        document.title = "Discograph: " + name;
        dg.graph.json = json;
        dg.updateForceLayout();
        dg.startForceLayout();
        setTimeout(function() {
            dg.graph.isUpdating = false;
        }, 2000);
    }

    dg.navigateGraph = function(id) {
        dg.history.pushState(id);
        dg.updateGraph(id);
    }

    dg.selectNode = function(id) {
        dg.graph.selectedNodeID = id;
        dg.graph.haloSelection
            .filter("*:not(.node-" + dg.graph.selectedNodeID + ")")
            .select(".halo")
            .style("fill-opacity", 0.);
        dg.graph.haloSelection
            .filter(".node-" + dg.graph.selectedNodeID)
            .select(".halo")
            .style("fill-opacity", 0.1);
        dg.graph.nodeSelection
            .filter("*:not(.node-" + dg.graph.selectedNodeID + ")")
            .style("stroke", "#fff");
        dg.graph.nodeSelection
            .filter("*:not(.node-" + dg.graph.selectedNodeID + ")")
            .select(".more")
            .style("fill", "#fff");
        dg.graph.nodeSelection
            .filter(".node-" + dg.graph.selectedNodeID)
            .style("stroke", "#000");
        dg.graph.nodeSelection
            .filter(".node-" + dg.graph.selectedNodeID)
            .select(".more")
            .style("fill", "#000");
        dg.graph.textSelection
            .filter(".node-" + dg.graph.selectedNodeID)
            .moveToFront();
    }

    function getOuterRadius(d) {
        if (0 < d.size) {
            return 12 + (Math.sqrt(d.size) * 2);
        }
        return 9 + (Math.sqrt(d.size) * 2);
    }

    function getInnerRadius(d) {
        return 9 + (Math.sqrt(d.size) * 2);
    }

    function onHaloEnter(haloEnter) {
        var haloEnter = haloEnter.append("g")
            .filter(function(d, i) { return !d.isIntermediate ? this : null })
            .attr("class", function(d) { return "node node-" + d.key; })
        haloEnter.append("circle")
            .attr("class", "halo")
            .attr("r", function(d) { return getOuterRadius(d) + 40; });
    }

    function onHaloExit(haloExit) {
        haloExit.remove();
    }

    function onLinkEnter(linkEnter) {
        var linkEnter = linkEnter.append("path")
            .filter(function(d, i) { return d.nodes !== undefined ? this : null })
            .attr("class", function(d) { return "link link-" + d.key; })
            .style("stroke-dasharray", function(d) {
                if (d.role == "Alias") {
                    return "2, 2";
                } else {
                    return "0, 0";
                }
            });
    }

    function onLinkExit(linkExit) {
        linkExit.remove();
    }

    function onNodeEnter(nodeEnter) {
        var nodeEnter = nodeEnter.append("g")
            .filter(function(d, i) { return !d.isIntermediate ? this : null })
            .attr("class", function(d) { return "node node-" + d.key; })
            .style("fill", function(d) { return dg.color.heatmap(d); })
            .call(dg.graph.forceLayout.drag);
        nodeEnter.on("mousedown", function(d) {
            if (!dg.graph.isUpdating) {
                dg.selectNode(d.id);
            }
        });
        nodeEnter.on("dblclick", function(d) {
            if (!dg.graph.isUpdating) {
                dg.navigateGraph(d.id);
            }
        });
        nodeEnter.select(function(d, i) {return 0 < d.size ? this : null; })
            .append("circle")
            .attr("class", "outer")
            .attr("r", getOuterRadius);
        nodeEnter.append("circle")
            .attr("class", "inner")
            .attr("r", getInnerRadius);
        nodeEnter.append("path")
            .attr("class", "more")
            .attr("d", d3.svg.symbol().type("cross").size(64))
            .style("stroke-width", 0)
            .style("fill-opacity", 1)
            .style("fill", "#fff")
            .style("opacity", function(d) {return 0 < d.missing ? 1 : 0; });
        nodeEnter.append("title")
            .text(function(d) { return d.name; });
    }

    function onNodeExit(nodeExit) {
        nodeExit.remove();
    }

    function onNodeUpdate(nodeSelection) {
        nodeSelection.transition()
            .duration(1000)
            .style("fill", function(d) { return dg.color.heatmap(d); })
        nodeSelection.selectAll(".more")
            .transition()
            .duration(1000)
            .style("opacity", function(d) {return 0 < d.missing ? 1 : 0; });
    }

    function onTextEnter(textEnter) {
        var textEnter = textEnter.append("g")
            .filter(function(d, i) { return !d.isIntermediate ? this : null })
            .attr("class", function(d) { return "node node-" + d.key; })
        textEnter.append("text")
            .attr("class", "outer")
            .attr("dy", ".35em")
            .attr("dx", function(d) { return getOuterRadius(d) + 3; })
            .text(function(d) { return d.name; });
        textEnter.append("text")
            .attr("class", "inner")
            .attr("dy", ".35em")
            .attr("dx", function(d) { return getOuterRadius(d) + 3; })
            .text(function(d) { return d.name; });
    }

    function onTextExit(textExit) {
        textExit.remove();
    }

    dg.startForceLayout = function() {
        dg.graph.forceLayout.start();
        dg.graph.haloSelection = dg.graph.haloSelection
            .data(dg.graph.nodes, function(d) { return d.key; });
        dg.graph.linkSelection = dg.graph.linkSelection
            .data(dg.graph.links, function(d) { return d.key; });
        dg.graph.nodeSelection = dg.graph.nodeSelection
            .data(dg.graph.nodes, function(d) { return d.key; });
        dg.graph.textSelection = dg.graph.textSelection
            .data(dg.graph.nodes, function(d) { return d.key; });

        var haloEnter = dg.graph.haloSelection.enter();
        var haloEnter2 = haloEnter.filter(function(d, i) { 
            return d.isIntermediate ? null : this;
        });
        onHaloEnter(haloEnter);
        onHaloExit(dg.graph.haloSelection.exit());

        var nodeEnter = dg.graph.nodeSelection.enter();
        onNodeEnter(nodeEnter);
        onNodeExit(dg.graph.nodeSelection.exit());
        onNodeUpdate(dg.graph.nodeSelection);

        var textEnter = dg.graph.textSelection.enter();
        onTextEnter(textEnter);
        onTextExit(dg.graph.textSelection.exit());

        var linkEnter = dg.graph.linkSelection.enter();
        onLinkEnter(linkEnter);
        onLinkExit(dg.graph.linkSelection.exit());

        dg.graph.svgSelection.transition()
            .duration(1000)
            .style("opacity", 1);
        dg.selectNode(dg.graph.centerNodeID);
    }

    function translate(d) { return "translate(" + d.x + "," + d.y + ")"; };

    function spline(d) {
        return "M" + d.nodes[0].x + "," + d.nodes[0].y
             + "S" + d.nodes[1].x + "," + d.nodes[1].y
             + " " + d.nodes[2].x + "," + d.nodes[2].y;
    }

    dg.tick = function() {
        dg.graph.linkSelection.filter(function(d, i) {
            return d.nodes !== undefined;
            })
            .attr("d", spline)
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        dg.graph.haloSelection.attr("transform", translate);
        dg.graph.nodeSelection.attr("transform", translate);
        dg.graph.textSelection.attr("transform", translate);
    }

    dg.updateForceLayout = function() {
        var json = dg.graph.json;

        var newNodeMap = d3.map();
        json.nodes.forEach(function(node) {
            node.key = node.id;
            newNodeMap.set(node.id, node);
        });

        var newLinkMap = d3.map();
        json.links.forEach(function(link) {
            var role = link.role.toLocaleLowerCase().replace(/\s+/g, "-");
            var key = link.source + "-" + role + "-" + link.target;
            var source = link.source,
                target = link.target,
                intermediate = {key: key, isIntermediate: true, size: 0};
            var siLink = {
                isPrimary: true,
                key: "(i)-" + key,
                role: link.role,
                source: source, 
                target: key, 
                nodes: [source, intermediate, target],
            };
            var itLink = {
                isPrimary: false,
                key: key + "-(i)",
                source: key, 
                target: target, 
            };
            link.intermediate = key;
            newNodeMap.set(key, intermediate);
            newLinkMap.set(siLink.key, siLink);
            newLinkMap.set(itLink.key, itLink);
        });

        // NODES
        var nodeKeysToRemove = [];
        dg.graph.nodeMap.keys().forEach(function(key) {
            if (!newNodeMap.has(key)) {
                nodeKeysToRemove.push(key);
            };
        });
        nodeKeysToRemove.forEach(function(key) {
            dg.graph.nodeMap.remove(key);
        });

        // LINKS
        var linkKeysToRemove = [];
        dg.graph.linkMap.keys().forEach(function(key) {
            if (!newLinkMap.has(key)) {
                linkKeysToRemove.push(key);
            };
        });
        linkKeysToRemove.forEach(function(key) {
            dg.graph.linkMap.remove(key);
        });

        // UPDATE NODE PROPERTIES
        newNodeMap.entries().forEach(function(entry) {
            var key = entry.key;
            var value = entry.value;
            if (dg.graph.nodeMap.has(key)) {
                if (!value.isIntermediate) {
                    var node = dg.graph.nodeMap.get(key);
                    node.distance = value.distance;
                    node.missing = value.missing;
                }
            } else {
                value.x = dg.graph.newNodeCoords[0] + (Math.random() * 100) - 50;
                value.y = dg.graph.newNodeCoords[1] + (Math.random() * 100) - 50;
                dg.graph.nodeMap.set(key, value);
            }
        });

        // UPDATE LINK REFERENCES
        newLinkMap.entries().forEach(function(entry) {
            if (!dg.graph.linkMap.has(entry.key)) {
                entry.value.source = dg.graph.nodeMap.get(entry.value.source);
                entry.value.target = dg.graph.nodeMap.get(entry.value.target);
                if (entry.value.nodes !== undefined) {
                    entry.value.nodes[0] = dg.graph.nodeMap.get(entry.value.nodes[0]);
                    entry.value.nodes[2] = dg.graph.nodeMap.get(entry.value.nodes[2]);
                }
                dg.graph.linkMap.set(entry.key, entry.value);
            }
        });

        // PUSH DATA
        dg.graph.nodes.length = 0;
        Array.prototype.push.apply(dg.graph.nodes, dg.graph.nodeMap.values());
        dg.graph.links.length = 0;
        Array.prototype.push.apply(dg.graph.links, dg.graph.linkMap.values());
        dg.graph.centerNodeID = json.center[0];
    }

    dg.updateGraph = function(id) {
        dg.graph.isUpdating = true;
        var foundNode = dg.graph.nodeSelection
            .filter(function(d) { return d.id == id; });
        if (foundNode.length == 1) {
            foundNode.each(function(d) {
                dg.graph.newNodeCoords = [d.x, d.y];
            });
        } else {
            dg.graph.newNodeCoords = [
                dg.graph.dimensions[0] / 2,
                dg.graph.dimensions[1] / 2,
            ];
        }
        dg.graph.svgSelection
            .transition()
            .duration(250)
            .style("opacity", 0.333);
        if (dg.graph.cache.has(id)) {
            var json = JSON.parse(JSON.stringify(dg.graph.cache.get(id)));
            dg.handleNewGraphData(null, json);
        } else {
            d3.json(dg.graph.APIURL + id, dg.handleNewGraphData);
        }
    }

    /* INITIALIZATION */

    dg.init = function() {
        d3.selection.prototype.moveToFront = function() {
            return this.each(function(){ this.parentNode.appendChild(this); });
        };

        window.addEventListener("popstate", dg.history.onPopState);

        var w = window,
            d = document,
            e = d.documentElement,
            g = d.getElementsByTagName('body')[0];
        dg.graph.dimensions = [
            w.innerWidth || e.clientWidth || g.clientWidth,
            w.innerHeight|| e.clientHeight|| g.clientHeight,
        ];
        dg.graph.newNodeCoords = [
            dg.graph.dimensions[0] / 2,
            dg.graph.dimensions[1] / 2,
        ];
        window.addEventListener("resize", function() {
            dg.graph.dimensions = [
                w.innerWidth || e.clientWidth || g.clientWidth,
                w.innerHeight|| e.clientHeight|| g.clientHeight,
            ];
            dg.graph.svgSelection
                .attr("width", dg.graph.dimensions[0])
                .attr("height", dg.graph.dimensions[1]);
            dg.graph.forceLayout.size(dg.graph.dimensions).start();
        });

        dg.graph.svgSelection = d3.select("body").append("svg")
            .attr("width", dg.graph.dimensions[0])
            .attr("height", dg.graph.dimensions[1]);
        dg.graph.haloLayer = dg.graph.svgSelection.append("g")
            .attr("id", "haloLayer");
        dg.graph.linkLayer = dg.graph.svgSelection.append("g")
            .attr("id", "linkLayer");
        dg.graph.nodeLayer = dg.graph.svgSelection.append("g")
            .attr("id", "nodeLayer");
        dg.graph.textLayer = dg.graph.svgSelection.append("g")
            .attr("id", "textLayer");

        dg.graph.haloSelection = dg.graph.haloLayer.selectAll(".node");
        dg.graph.linkSelection = dg.graph.linkLayer.selectAll(".link");
        dg.graph.nodeSelection = dg.graph.nodeLayer.selectAll(".node");
        dg.graph.textSelection = dg.graph.textLayer.selectAll(".node");

        dg.graph.forceLayout = d3.layout.force()
            .nodes(dg.graph.nodes)
            .links(dg.graph.links)
            .linkStrength(1)
            .friction(0.95)
            .linkDistance(50)
            .charge(function(d, i) {
                return d.isIntermediate ? -50 : -150;
            })
            .gravity(0.1)
            .theta(0.9)
            .alpha(0.1)
            .size(dg.graph.dimensions)
            .on("tick", dg.tick);

        console.log('Discograph initialized.')
    }
    this.dg = dg;
    dg.init();
}();

dg.navigateGraph(d3.select("body").attr("id"));