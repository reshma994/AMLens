import {
  useEffect,
  useRef,
} from "react";

import cytoscape from "cytoscape";


function NetworkGraph({
  graph,
  accounts,
  selectedAccount,
  onSelectAccount,
}) {
  const containerRef =
    useRef(null);

  const cyRef =
    useRef(null);


  /*
  |--------------------------------------------------------------------------
  | Build graph
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    if (!graph || !containerRef.current) {
      return;
    }


    const accountMap =
      new Map(
        accounts.map(
          (account) => [
            account.account_id,
            account,
          ]
        )
      );


    const elements = [

      ...graph.nodes.map(
        (node) => {

          const account =
            accountMap.get(node.id);

          return {
            data: {
              id: node.id,

              label: node.id,

              riskScore:
                account?.risk_score ?? 0,

              riskLevel:
                account?.risk_level ??
                "LOW",
            },
          };
        }
      ),


      ...graph.edges.map(
        (edge) => ({
          data: {
            id: edge.id,

            source: edge.source,

            target: edge.target,

            amountMinor:
              edge.amount_minor,

            timestamp:
              edge.timestamp,
          },
        })
      ),
    ];


    if (cyRef.current) {
      cyRef.current.destroy();
    }


    const cy =
      cytoscape({
        container:
          containerRef.current,

        elements,

        layout: {
          name: "circle",

          fit: true,

          padding: 70,

          avoidOverlap: true,
        },


        minZoom: 0.35,

        maxZoom: 2.5,


        style: [

          {
            selector: "node",

            style: {

              "background-color":
                "#162a40",

              "border-width": 1,

              "border-color":
                "#35516e",

              color:
                "#dce7f3",

              label:
                "data(label)",

              "font-size": 10,

              "font-weight": 600,

              "text-valign": "center",

              "text-halign": "center",

              width: 38,

              height: 38,

              "overlay-opacity": 0,

            },
          },


          {
            selector:
              'node[riskLevel = "CRITICAL"]',

            style: {
              "background-color":
                "#5b2025",

              "border-color":
                "#ef4444",

              "border-width": 2,

              color:
                "#fff1f2",
            },
          },


          {
            selector:
              'node[riskLevel = "HIGH"]',

            style: {
              "background-color":
                "#4a2a18",

              "border-color":
                "#f97316",

              color:
                "#fff7ed",
            },
          },


          {
            selector:
              'node[riskLevel = "MEDIUM"]',

            style: {
              "background-color":
                "#423814",

              "border-color":
                "#eab308",

              color:
                "#fefce8",
            },
          },


          {
            selector:
              'node[riskLevel = "LOW"]',

            style: {
              "background-color":
                "#14283a",

              "border-color":
                "#35516e",
            },
          },


          {
            selector: "edge",

            style: {

              width: 1.5,

              "line-color":
                "#42617f",

              "target-arrow-color":
                "#42617f",

              "target-arrow-shape":
                "triangle",

              "curve-style":
                "bezier",

              "arrow-scale":
                0.7,

              opacity: 0.72,
            },
          },


          {
            selector:
              ".evidence-edge",

            style: {

              width: 3,

              "line-color":
                "#60a5fa",

              "target-arrow-color":
                "#60a5fa",

              opacity: 1,
            },
          },


          {
            selector:
              ".faded-edge",

            style: {
              opacity: 0.12,
            },
          },


          {
            selector:
              ".selected-node",

            style: {

              "border-color":
                "#60a5fa",

              "border-width": 3,

              "background-color":
                "#173d63",

              "shadow-blur": 18,

              "shadow-color":
                "#3b82f6",

              "shadow-opacity": 0.35,
            },
          },


          {
            selector:
              ".selected-edge",

            style: {

              width: 3,

              "line-color":
                "#f8fafc",

              "target-arrow-color":
                "#f8fafc",

              opacity: 1,
            },
          },

        ],
      });


    cyRef.current = cy;


    /*
    |--------------------------------------------------------------------------
    | Node selection
    |--------------------------------------------------------------------------
    */

    cy.on(
      "tap",
      "node",
      (event) => {

        const node =
          event.target;

        onSelectAccount(
          node.id()
        );
      }
    );


    /*
    |--------------------------------------------------------------------------
    | Edge selection
    |--------------------------------------------------------------------------
    */

    cy.on(
      "tap",
      "edge",
      (event) => {

        const edge =
          event.target;

        const data =
          edge.data();

        console.log(
          "Transaction:",
          data.id,
          data.amountMinor,
          data.timestamp
        );

        cy.elements()
          .removeClass(
            "selected-edge"
          );

        edge.addClass(
          "selected-edge"
        );
      }
    );


    return () => {
      cy.destroy();
      cyRef.current = null;
    };

  }, [
    graph,
    accounts,
    onSelectAccount,
  ]);


  /*
  |--------------------------------------------------------------------------
  | Highlight selected account
  |--------------------------------------------------------------------------
  */

  useEffect(() => {

    const cy =
      cyRef.current;

    if (!cy) {
      return;
    }


    cy.nodes()
      .removeClass(
        "selected-node"
      );

    cy.edges()
      .removeClass(
        "evidence-edge"
      );

    cy.edges()
      .removeClass(
        "faded-edge"
      );


    if (!selectedAccount) {
      return;
    }


    const selectedNode =
      cy.getElementById(
        selectedAccount
      );


    if (!selectedNode.length) {
      return;
    }


    selectedNode.addClass(
      "selected-node"
    );


    const account =
      accounts.find(
        (item) =>
          item.account_id ===
          selectedAccount
      );


    if (!account) {
      return;
    }


    const evidenceIds =
      new Set(
        account.reasons.flatMap(
          (reason) =>
            reason.transaction_ids ||
            []
        )
      );


    cy.edges().forEach(
      (edge) => {

        if (
          evidenceIds.has(
            edge.id()
          )
        ) {
          edge.addClass(
            "evidence-edge"
          );
        } else {
          edge.addClass(
            "faded-edge"
          );
        }

      }
    );


  }, [
    selectedAccount,
    accounts,
  ]);


  return (
    <section className="panel graph-panel">

      <div className="panel-header">

        <div>

          <h3>
            Transaction Network
          </h3>

          <p>
            Directed transaction relationships
          </p>

        </div>


        <div className="graph-controls">

          <span>
            {graph?.nodes?.length || 0}
            {" "}accounts
          </span>

          <span>
            {graph?.edges?.length || 0}
            {" "}transactions
          </span>

        </div>

      </div>


      <div
        ref={containerRef}
        className="graph-container"
      >

        {!graph && (
          <div className="graph-empty">

            <div className="graph-empty-icon">
              ◇
            </div>

            <strong>
              Transaction network
            </strong>

            <p>
              Load an analysis to visualize
              transaction relationships.
            </p>

          </div>
        )}

      </div>

    </section>
  );
}


export default NetworkGraph;