const USE_MOCKS =
  import.meta.env.VITE_USE_MOCKS !== "false";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";


/*
|--------------------------------------------------------------------------
| Mock Analysis
|--------------------------------------------------------------------------
|
| Temporary frontend fixture.
|
| This allows the complete UI to be developed before the FastAPI backend
| is connected.
|
| The structure matches the AMLens API contract.
|
*/

const MOCK_ANALYSIS = {
  analysis_id: "demo-001",

  created_at: "2026-01-01T12:00:00Z",

  engine_version: "rules-v1",

  currency: "INR",

  summary: {
    total_accounts: 22,
    total_transactions: 17,
    total_volume_minor: 238500000,
    alert_count: 6,
    high_risk_accounts: 2,
  },

  accounts: [
    {
      account_id: "A",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "B",
      risk_score: 100,
      risk_level: "CRITICAL",
      reasons: [
        {
          code: "CIRCULAR_FLOW",
          points: 60,
          transaction_ids: [
            "T01",
            "T02",
            "T03",
            "T04",
          ],
        },
        {
          code: "RAPID_PASS_THROUGH",
          points: 40,
          transaction_ids: [
            "T01",
            "T02",
          ],
        },
      ],
    },

    {
      account_id: "C",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "D",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "E",
      risk_score: 72,
      risk_level: "HIGH",
      reasons: [
        {
          code: "RAPID_PASS_THROUGH",
          points: 40,
          transaction_ids: [
            "T05",
            "T06",
          ],
        },
      ],
    },

    {
      account_id: "F",
      risk_score: 64,
      risk_level: "HIGH",
      reasons: [
        {
          code: "CIRCULAR_FLOW",
          points: 60,
          transaction_ids: [
            "T07",
            "T08",
            "T09",
            "T10",
          ],
        },
      ],
    },

    {
      account_id: "G",
      risk_score: 48,
      risk_level: "MEDIUM",
      reasons: [
        {
          code: "RAPID_PASS_THROUGH",
          points: 40,
          transaction_ids: [
            "T11",
            "T12",
          ],
        },
      ],
    },

    {
      account_id: "H",
      risk_score: 42,
      risk_level: "MEDIUM",
      reasons: [
        {
          code: "RAPID_PASS_THROUGH",
          points: 40,
          transaction_ids: [
            "T13",
            "T14",
          ],
        },
      ],
    },

    {
      account_id: "I",
      risk_score: 35,
      risk_level: "MEDIUM",
      reasons: [],
    },

    {
      account_id: "J",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "K",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "L",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "M",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "N01",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "O",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "P",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "Q",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "R",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "S",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "T",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "U",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },

    {
      account_id: "V",
      risk_score: 0,
      risk_level: "LOW",
      reasons: [],
    },
  ],

  graph: {
    nodes: [
      "A",
      "B",
      "C",
      "D",
      "E",
      "F",
      "G",
      "H",
      "I",
      "J",
      "K",
      "L",
      "N01",
      "O",
      "P",
      "Q",
      "R",
      "S",
      "T",
      "U",
      "V",
      "M",
    ].map((id) => ({
      id,
    })),

    edges: [
      {
        id: "T01",
        source: "A",
        target: "B",
        amount_minor: 50000000,
        timestamp: "2026-01-01T10:00:00Z",
      },

      {
        id: "T02",
        source: "B",
        target: "C",
        amount_minor: 49000000,
        timestamp: "2026-01-01T10:03:00Z",
      },

      {
        id: "T03",
        source: "C",
        target: "D",
        amount_minor: 48000000,
        timestamp: "2026-01-01T10:06:00Z",
      },

      {
        id: "T04",
        source: "D",
        target: "A",
        amount_minor: 47000000,
        timestamp: "2026-01-01T10:09:00Z",
      },

      {
        id: "T05",
        source: "E",
        target: "G",
        amount_minor: 18000000,
        timestamp: "2026-01-01T11:00:00Z",
      },

      {
        id: "T06",
        source: "G",
        target: "H",
        amount_minor: 17500000,
        timestamp: "2026-01-01T11:04:00Z",
      },

      {
        id: "T07",
        source: "F",
        target: "I",
        amount_minor: 15000000,
        timestamp: "2026-01-01T12:00:00Z",
      },

      {
        id: "T08",
        source: "I",
        target: "J",
        amount_minor: 14000000,
        timestamp: "2026-01-01T12:05:00Z",
      },

      {
        id: "T09",
        source: "J",
        target: "K",
        amount_minor: 13000000,
        timestamp: "2026-01-01T12:10:00Z",
      },

      {
        id: "T10",
        source: "K",
        target: "F",
        amount_minor: 12000000,
        timestamp: "2026-01-01T12:15:00Z",
      },

      {
        id: "T11",
        source: "G",
        target: "L",
        amount_minor: 11000000,
        timestamp: "2026-01-01T13:00:00Z",
      },

      {
        id: "T12",
        source: "L",
        target: "M",
        amount_minor: 10500000,
        timestamp: "2026-01-01T13:05:00Z",
      },

      {
        id: "T13",
        source: "H",
        target: "O",
        amount_minor: 9000000,
        timestamp: "2026-01-01T14:00:00Z",
      },

      {
        id: "T14",
        source: "O",
        target: "P",
        amount_minor: 8500000,
        timestamp: "2026-01-01T14:04:00Z",
      },

      {
        id: "T15",
        source: "Q",
        target: "R",
        amount_minor: 5000000,
        timestamp: "2026-01-01T15:00:00Z",
      },

      {
        id: "T16",
        source: "R",
        target: "S",
        amount_minor: 4500000,
        timestamp: "2026-01-01T15:05:00Z",
      },

      {
        id: "T17",
        source: "T",
        target: "U",
        amount_minor: 3000000,
        timestamp: "2026-01-01T16:00:00Z",
      },
    ],
  },

  alerts: [
    {
      id: "AL-B",
      account_id: "B",
      status: "OPEN",
      updated_at: "2026-01-01T12:00:00Z",
    },

    {
      id: "AL-E",
      account_id: "E",
      status: "OPEN",
      updated_at: "2026-01-01T12:00:00Z",
    },

    {
      id: "AL-F",
      account_id: "F",
      status: "OPEN",
      updated_at: "2026-01-01T12:00:00Z",
    },

    {
      id: "AL-G",
      account_id: "G",
      status: "OPEN",
      updated_at: "2026-01-01T12:00:00Z",
    },

    {
      id: "AL-H",
      account_id: "H",
      status: "OPEN",
      updated_at: "2026-01-01T12:00:00Z",
    },

    {
      id: "AL-I",
      account_id: "I",
      status: "OPEN",
      updated_at: "2026-01-01T12:00:00Z",
    },
  ],
};


/*
|--------------------------------------------------------------------------
| Helper
|--------------------------------------------------------------------------
*/

function wait(milliseconds) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}


/*
|--------------------------------------------------------------------------
| Upload CSV
|--------------------------------------------------------------------------
*/

export async function uploadCsv(file) {
  if (USE_MOCKS) {
    await wait(700);

    return structuredClone(MOCK_ANALYSIS);
  }

  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/analyses`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error(
      `Upload failed with status ${response.status}`
    );
  }

  return response.json();
}


/*
|--------------------------------------------------------------------------
| Get Analysis
|--------------------------------------------------------------------------
*/

export async function getAnalysis(analysisId) {
  if (USE_MOCKS) {
    await wait(300);

    if (analysisId !== "demo-001") {
      throw new Error("Analysis not found.");
    }

    return structuredClone(MOCK_ANALYSIS);
  }

  const response = await fetch(
    `${API_BASE_URL}/api/analyses/${analysisId}`
  );

  if (!response.ok) {
    throw new Error(
      `Unable to load analysis (${response.status}).`
    );
  }

  return response.json();
}


/*
|--------------------------------------------------------------------------
| Update Alert
|--------------------------------------------------------------------------
*/

export async function updateAlert(
  analysisId,
  alertId,
  status
) {
  if (USE_MOCKS) {
    await wait(400);

    return {
      id: alertId,
      account_id: MOCK_ANALYSIS.alerts.find(
        (alert) => alert.id === alertId
      )?.account_id,
      status,
      updated_at: new Date().toISOString(),
    };
  }

  const response = await fetch(
    `${API_BASE_URL}/api/analyses/${analysisId}/alerts/${alertId}`,
    {
      method: "PATCH",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        status,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Unable to update alert (${response.status}).`
    );
  }

  return response.json();
}