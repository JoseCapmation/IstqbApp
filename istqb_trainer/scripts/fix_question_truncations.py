"""
Apply fixes to data/questions.json: watermarks, mojibake, known truncated stems/options.
Run from istqb_trainer: py scripts/fix_question_truncations.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "questions.json"

WATERMARK = re.compile(
    r"\s*\d*\s*www\.istqb\.guru\s+ISTQB Sample Papers\s+\[[^\]]+\]\s*",
    re.I,
)


def clean_watermark(s: str) -> str:
    return WATERMARK.sub(" ", s).strip()


def clean_text(s: str) -> str:
    s = clean_watermark(s)
    s = s.replace("person' s", "person's").replace("person\u2019 s", "person's")
    s = s.replace("\ufffd", "'")
    return s


# question_id -> {"question": optional str, "options": optional dict}
PATCHES: dict[str, dict] = {
    "guru_17": {
        "options": {
            "B": "Two more test cases will be required for 100 % statement coverage, one of which will be required for 100 % decision coverage.",
            "D": "One more test case will be required for 100 % statement coverage.",
        }
    },
    "guru_20": {
        "options": {
            "A": "Confirmation testing is testing fixes to a set of defects and Regression testing is testing to detect defects in unchanged parts of the software after a change has been made",
            "B": "Confirmation testing is testing to establish whether any defects have been introduced as a result of changes, and Regression testing is testing unchanged parts of the software",
            "C": "Confirmation testing and Regression testing are both testing to establish whether any defects have been introduced as a result of changes",
        }
    },
    "guru_28": {
        "options": {
            "B": "Preventative tests are designed early; reactive tests are designed after the software has been produced",
            "D": "Preventative tests are designed after the software has been produced; reactive tests are designed early in the life cycle",
        }
    },
    "guru_46": {
        "options": {
            "A": "Testers spend more energy early in the product trying to find bugs than preparing to do a good job testing later",
            "B": "Managers might not realize that the testing effort is ineffective, late in the project, when it is too late to do anything practical about it",
            "C": "It can increase the end-of-project pressure on testers to not find bugs, or to not report bugs",
        }
    },
    "guru_49": {
        "options": {
            "A": "The failure occurs only if you reach a statement taking the TRUE branch of an IF statement, while the FALSE branch is not tested",
            "B": "The failure depends on the program's inability to handle specific data values, rather than on the program's control structure",
        }
    },
    "guru_50": {
        "options": {
            "A": "Even though the numbers you look at appear better, to achieve these numbers, people may do things that skew the measurements",
            "B": "We don't know how to measure a variable (our measurement is dysfunctional) and so we don't know what to do",
        }
    },
    "guru_51": {
        "options": {
            "B": "We have no definite stopping point for testing, which makes it easier for some managers to argue for very little testing",
            "C": "We have no easy answer for what testing tasks should always be required, because every task you skip could let serious bugs slip through",
        }
    },
    "guru_44": {"question": "Which is the best definition of complete testing?"},
    "guru_54": {"question": "Contract and regulation testing is a part of:"},
    "guru_65": {"question": "Which of the following is the standard for software product quality?"},
    "guru_70": {
        "options": {
            "A": "Confront the person and ask that other team members be allowed to express their opinions",
            "B": "Wait for the person to pause, acknowledge the person's opinion, and ask for someone else's opinion",
            "D": "Express an opinion that differs from the person's opinion in order to encourage others to speak",
        }
    },
    "guru_72": {"question": "A software model that can't be used in functional testing:"},
    "guru_79": {"question": "The software engineer's role in tool selection is:"},
    "guru_80": {"question": "Which is not the fundamental test process?"},
    "guru_84": {
        "options": {
            "B": "To measure the size of the functionality of an information system",
        }
    },
    "guru_102": {
        "options": {
            "B": "An input or output range of values such that only one value in the range becomes a test input",
            "D": "An input or output range of values such that every tenth value in the range becomes a test input",
        }
    },
    "guru_110": {
        "options": {
            "A": "Are most useful in uncovering defects in the process flows during real world use of the system",
            "B": "Are most useful in uncovering defects in the process flows during the testing use of the system",
            "C": "Are most useful in covering the defects in the process flows during real world use of the system",
        }
    },
    "guru_115": {"question": "Which of the following is a key characteristic of walkthrough?"},
    "guru_127": {
        "question": "What's the disadvantage of black box testing?",
        "options": {
            "C": "It is difficult to identify all possible inputs in limited testing time, so writing test cases is slow and difficult",
        },
    },
    "guru_144": {"question": "What type of tools are used for regression testing?"},
    "guru_147": {
        "options": {
            "A": "Unit, integration, system, acceptance",
            "B": "System, integration, unit, acceptance",
            "C": "Unit, integration, acceptance, system",
        }
    },
    "guru_150": {"question": "The principal attributes of tools and automation are:"},
    "guru_165": {
        "options": {
            "A": "Computer Aided Software Testing (CAST)",
        }
    },
    "guru_188": {
        "question": "An input field takes the year of birth between 1900 and 2004. The boundary values for testing this field are:"
    },
    "guru_190": {"question": "A common test technique during component test is:"},
    "guru_197": {
        "options": {
            "A": "You shorten the time required for testing",
        }
    },
    "guru_201": {"question": "The inputs for developing a test plan are taken from:"},
    "guru_204": {
        "options": {
            "B": "Component testing is also known as isolation or module testing",
        }
    },
    "guru_208": {
        "options": {
            "B": "A black box testing technique that can only be used during system testing",
        }
    },
    "guru_209": {"options": {"B": "It may be difficult to repeat the test"}},
    "guru_210": {"options": {"C": "The answer depends on the maturity of your developers"}},
    "guru_216": {"options": {"D": "Can only be run during user acceptance testing"}},
    "guru_220": {"question": "The difference between re-testing and regression testing is:"},
    "guru_226": {
        "options": {
            "B": "Increases as we move the product towards live use",
            "C": "Decreases as we move the product towards live use",
        }
    },
    "guru_233": {
        "options": {
            "D": "To allow the managers to see what projects it should be used in",
        }
    },
    "guru_234": {"question": "Which of the following is not part of performance testing:"},
    "guru_252": {"options": {"A": "Only important in system testing"}},
    "guru_253": {
        "options": {
            "C": "Performed by an independent test team",
            "D": "Useful to test bespoke software",
        }
    },
    "guru_258": {"question": "The place to start if you want a (new) test tool is:"},
    "guru_259": {"options": {"A": "As the first approach to deriving test cases"}},
    "guru_268": {
        "options": {
            "A": "Equivalence partitioning, Decision Table and Control flow are white box testing",
            "B": "Equivalence partitioning, Boundary Value Analysis, Data Flow are black box testing",
            "C": "Equivalence partitioning, State Transition, Use Case Testing are black box testing",
            "D": "Equivalence partitioning, State Transition, Use Case Testing and Decision Table are black box testing",
        }
    },
    "guru_272": {
        "question": (
            "The selection of a test approach should consider the context: "
            "i. Risk of failure of the project, hazards to the product and risks of product failure to humans "
            "ii. Skills and experience of the people in the proposed techniques and tools "
            "iii. The objective of the testing and the mission of the testing team "
            "iv. The size of the team"
        )
    },
    "guru_273": {
        "options": {
            "A": "Independent testers are much more qualified than developers",
            "D": "Independent testers can test better than developers",
        }
    },
    "guru_277": {"options": {"D": "Different tools to perform regression testing"}},
    "guru_290": {"options": {"A": "Designed by persons who write the software under test"}},
    "guru_292": {
        "question": (
            "Deciding how much testing is enough should take into account: "
            "i. Level of risk including technical and business product and project risk "
            "ii. Project constraints such as time and budget "
            "iii. Size of the testing team "
            "iv. Size of the test items"
        )
    },
    "guru_324": {"question": "A standard for software testing terminology is:"},
    "guru_330": {"question": "Amount of testing performed will not depend on:"},
    "guru_336": {
        "options": {
            "B": "If you find a lot of bugs in testing, you should not be very confident about the quality of software"
        }
    },
    "guru_340": {
        "options": {
            "A": "A process for selecting test cases",
            "C": "A way to measure the quality of software",
        }
    },
    "guru_342": {
        "options": {
            "B": "Should be newly constructed for each new version of the software",
            "C": "Is needed only until the software is released into production or use",
            "D": "Does not need to be documented and commented, as it does not form part of the release",
        }
    },
    "guru_351": {"question": "When reporting faults found to developers, testers should be:"},
    "guru_352": {
        "options": {
            "A": "Performance testing can be done during unit testing as well as during the testing of whole systems",
            "B": "The acceptance test does not necessarily include a regression test",
        }
    },
    "guru_355": {
        "options": {
            "C": "Branch coverage should be mandatory for all software",
            "D": "Can only be applied at unit or module testing, not at system testing",
        }
    },
    "guru_361": {"question": "A program with high cyclomatic complexity is almost likely to be:"},
    "guru_363": {
        "options": {
            "A": "State transition testing, code testing, agile testing",
            "B": "Equivalence partitioning, state transition testing, decision table testing",
            "D": "System integration testing, system testing, decision table testing",
        }
    },
    "guru_365": {
        "options": {
            "B": "A goal is to find as many failures as possible so that the cause of the failures can be identified and fixed"
        }
    },
    "guru_366": {
        "options": {
            "D": "It is led by the author, uses checklists, and collects data for improvement",
        }
    },
    "guru_367": {
        "options": {
            "B": "Because errors are frequently made during programming of the different cases near the boundaries of equivalence classes",
            "C": "Because only equivalence classes that are equal from a functional point of view are considered",
        }
    },
    "guru_370": {
        "options": {
            "B": "Only functional requirements are tested; non-functional requirements are validated in a separate activity",
            "C": "Only non-functional requirements are tested; functional requirements are validated in a separate activity",
        }
    },
    "guru_372": {"options": {"A": "A walkthrough does not follow a defined process"}},
    "guru_373": {
        "options": {
            "A": "Because testing is a good method to make sure there are no defects in the software",
            "B": "Because verification and validation are not enough to get to know the quality of the software",
            "C": "Because testing measures the quality of the software system and helps to increase the quality",
        }
    },
    "guru_374": {
        "options": {
            "B": "With automated testing you can make statements with more confidence about the quality of the software",
            "C": "For a software system, it is not possible, under normal conditions, to test all input and output combinations",
        }
    },
    "guru_378": {"options": {"D": "Less than 0, 1 through 14, 15 and more"}},
    "guru_380": {
        "options": {
            "C": "The messages for user input errors are misleading and not helpful for understanding the problem",
            "D": "Under high load, the system does not provide enough open ports to connect to",
        }
    },
    "guru_381": {"options": {"A": "Static analysis tools are used only by developers"}},
    "guru_382": {
        "options": {
            "A": "Interoperability (compatibility) testing, reliability testing, performance testing",
            "B": "System testing, performance testing",
            "C": "Load testing, stress testing, component testing, portability testing",
            "D": "Testing various configurations, beta testing, load testing",
        }
    },
    "guru_383": {
        "options": {
            "C": "Percentage of completed tasks in the preparation of test environment; test cases developed"
        }
    },
    "guru_384": {
        "options": {
            "C": "Only the test object. The test cases need to be adapted during agile testing",
        }
    },
    "guru_390": {
        "options": {
            "B": "Configuration management systems allow us to provide accurate defect statistics of the software being tested"
        }
    },
    "guru_392": {"options": {"D": "Ideas for the test case improvement"}},
    "guru_393": {"options": {"C": "Triggered by modifications, migration or retirement of existing software"}},
    "guru_395": {
        "options": {
            "A": "A software development model that illustrates how testing activities integrate with software development activities",
            "B": "A software life-cycle model that is not relevant for testing",
        }
    },
    "guru_399": {
        "question": "The _______ testing should include operational tests of the new environment as well as of the changed software:"
    },
    "guru_409": {"question": "Test basis documentation is analyzed in which phase of testing?"},
    "guru_415": {"question": "Verification activities during design stages are:"},
    "guru_416": {"question": "Equivalence partitioning consists of various activities:"},
    "guru_427": {
        "options": {
            "B": "Details what types of tests must be conducted, what stages of testing are required and documents schedules"
        }
    },
    "guru_429": {
        "question": "If the application is complex, but NOT data intensive and is to be tested on one configuration and 2 rounds, the easiest method to test is:"
    },
    "guru_435": {"question": "Review is one of the methods of V&V. The other methods are:"},
    "guru_442": {"options": {"C": "Combination of alpha and beta testing"}},
    "guru_459": {
        "options": {
            "D": "A minimal test set that achieves 100% statement coverage will generally detect more faults than one that achieves 100% branch coverage"
        }
    },
    "guru_464": {
        "options": {
            "C": "Faults are cheapest to find in the early development phases but the most expensive to fix later",
            "D": "Although faults are most expensive to find during early development phases, they are cheapest to fix then",
        }
    },
    "guru_470": {"question": "In prioritising what to test, the most important objective is to:"},
    "guru_478": {
        "options": {
            "B": "Discussions with the development team",
            "C": "Time allocated for regression testing",
        }
    },
    "guru_489": {
        "options": {
            "A": "An independent tester may find defects more quickly than the person who wrote the software",
            "B": "An independent tester may be more focused on showing how the software works than the person who wrote it",
        }
    },
    "guru_500": {
        "options": {
            "A": "Exercise system functions in proportion to the frequency they will be used in production",
            "B": "Push the system beyond its designed operation limits and are likely to make the system fail",
            "D": "Exercise the most complicated and the most error-prone portions of the system",
        }
    },
}

PATCHES["guru_293"] = {
    "question": "Which of the following will be the best definition for testing?",
    "options": {
        "C": "The purpose of testing is to demonstrate that the program does what it is supposed to do",
    },
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    for block in data:
        for q in block.get("questions") or []:
            qid = q.get("id")
            if "question" in q and isinstance(q["question"], str):
                q["question"] = clean_text(q["question"])
            opts = q.get("options") or {}
            for k in list(opts.keys()):
                if isinstance(opts[k], str):
                    opts[k] = clean_text(opts[k])

            if qid in PATCHES:
                patch = PATCHES[qid]
                if "question" in patch:
                    q["question"] = patch["question"]
                if "options" in patch:
                    for ok, ov in patch["options"].items():
                        q.setdefault("options", {})[ok] = ov

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Updated", PATH)


if __name__ == "__main__":
    main()
