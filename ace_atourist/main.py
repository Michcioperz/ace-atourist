from ninja_syntax import Writer
from pathlib import Path


def get_test_ins():
    for inpath in Path("tests").glob("*.in"):
        stem = inpath.stem
        outpath = inpath.with_suffix(".out")
        if inpath.is_file() and outpath.is_file():
            yield inpath


def main():
    with open("build.ninja", "w") as f:
        ninja = Writer(f)
        ninja.include("config.ninja")
        ninja.rule(
            "rustc",
            "rustc -o $out -g --edition 2018 -C codegen-units=1 -C lto=fat -C target-cpu=x86-64 -C opt-level=3 -C target-feature=+crt-static -C panic=abort $in",
        )
        ninja.rule(
            "gplusplus", "g++ -o $out -static -O3 -g -march=x86-64 -std=c++17 $in"
        )
        ninja.rule(
            "zig",
            "zig build-exe --output-dir tmp --single-threaded -mcpu x86_64 --release-fast $in",
        )
        ninja.rule(
            "oiejq-bin",
            "sio2jail --mount-namespace off --pid-namespace off --uts-namespace off --ipc-namespace off --net-namespace off -s -f 3 -o oiaug -m $mem --instruction-count-limit $instr -- ./$exe <$inp >$outp 2>$errp 3>$infp",
        )
        customCompareSourceExists = False  # TODO
        customCompare = False
        if Path("custom-compare").exists() or customCompareSourceExists:
            ninja.rule(
                "diff",
                "./custom-compare $in >/dev/null && echo 1 > $out || echo 0 > $out",
            )
            customCompare = True
        else:
            ninja.rule(
                "diff", "diff -Z -q $in >/dev/null && echo 1 > $out || echo 0 > $out"
            )
        ninja.rule("sum", "cat $in | paste -sd+ | bc >$out")
        ninja.rule("extract-status", "awk 'NR <= 1 { print $$1 }' $in >$out")
        ninja.rule("extract-exitcode", "awk 'NR <= 1 { print $$2 }' $in >$out")
        ninja.rule("extract-time", "awk 'NR <= 1 { print $$3 }' $in >$out")
        ninja.rule("extract-memory", "awk 'NR <= 1 { print $$5 }' $in >$out")
        ninja.rule("extract-syscalls", "awk 'NR <= 1 { print $$6 }' $in >$out")
        ninja.rule("make-a-list", "echo $in | xargs -n1 echo > $out")

        ins = list(get_test_ins())
        progs = []
        tmp = Path("tmp")
        ninja.build([str(tmp / "test_list")], "make-a-list", [str(x) for x in ins])
        for src in Path("programs").glob("*.rs"):
            prog_stem = src.stem
            ninja.build([str(tmp / prog_stem)], "rustc", [str(src)])
            progs.append(str(src))
            corrs = []
            timps = []
            memps = []
            for infile in ins:
                outfile = str(infile.with_suffix(".out"))
                test_stem = infile.stem
                outp = str(tmp / f"{prog_stem}.{test_stem}.out")
                errp = str(tmp / f"{prog_stem}.{test_stem}.err")
                infp = str(tmp / f"{prog_stem}.{test_stem}.inf")
                corr = str(tmp / f"{prog_stem}.{test_stem}.corr")
                corrs.append(corr)
                ninja.build(
                    [outp, errp, infp],
                    "oiejq-bin",
                    [str(tmp / prog_stem), str(infile)],
                    variables=dict(
                        inp=str(infile),
                        outp=outp,
                        errp=errp,
                        infp=infp,
                        exe=str(tmp / prog_stem),
                    ),
                )
                ninja.build(
                    [corr],
                    "diff",
                    [outfile, outp],
                    ["custom-compare"] if customCompare else [],
                )
                timp = str(tmp / f"{prog_stem}.{test_stem}.tim")
                memp = str(tmp / f"{prog_stem}.{test_stem}.mem")
                timps.append(timp)
                memps.append(memp)
                ninja.build([memp], "extract-memory", [infp])
                ninja.build([timp], "extract-time", [infp])
            ninja.build([prog_stem + ".memsum"], "sum", memps)
            ninja.build([prog_stem + ".timesum"], "sum", timps)
            ninja.build([prog_stem + ".corrects"], "sum", corrs)
        for src in Path("programs").glob("*.cpp"):
            prog_stem = src.stem
            ninja.build([str(tmp / prog_stem)], "gplusplus", [str(src)])
            progs.append(str(src))
            corrs = []
            timps = []
            memps = []
            for infile in ins:
                outfile = str(infile.with_suffix(".out"))
                test_stem = infile.stem
                outp = str(tmp / f"{prog_stem}.{test_stem}.out")
                errp = str(tmp / f"{prog_stem}.{test_stem}.err")
                infp = str(tmp / f"{prog_stem}.{test_stem}.inf")
                corr = str(tmp / f"{prog_stem}.{test_stem}.corr")
                corrs.append(corr)
                ninja.build(
                    [outp, errp, infp],
                    "oiejq-bin",
                    [str(tmp / prog_stem), str(infile)],
                    variables=dict(
                        inp=str(infile),
                        outp=outp,
                        errp=errp,
                        infp=infp,
                        exe=tmp / prog_stem,
                    ),
                )
                ninja.build(
                    [corr],
                    "diff",
                    [outfile, outp],
                    ["custom-compare"] if customCompare else [],
                )
                timp = str(tmp / f"{prog_stem}.{test_stem}.tim")
                memp = str(tmp / f"{prog_stem}.{test_stem}.mem")
                timps.append(timp)
                memps.append(memp)
                ninja.build([memp], "extract-memory", [infp])
                ninja.build([timp], "extract-time", [infp])
            ninja.build([prog_stem + ".memsum"], "sum", memps)
            ninja.build([prog_stem + ".timesum"], "sum", timps)
            ninja.build([prog_stem + ".corrects"], "sum", corrs)
        for src in Path("programs").glob("*.zig"):
            prog_stem = src.stem
            ninja.build(
                [str(tmp / prog_stem), str((tmp / prog_stem).with_suffix(".o"))],
                "zig",
                [str(src)],
            )
            progs.append(str(src))
            corrs = []
            timps = []
            memps = []
            for infile in ins:
                outfile = str(infile.with_suffix(".out"))
                test_stem = infile.stem
                outp = str(tmp / f"{prog_stem}.{test_stem}.out")
                errp = str(tmp / f"{prog_stem}.{test_stem}.err")
                infp = str(tmp / f"{prog_stem}.{test_stem}.inf")
                corr = str(tmp / f"{prog_stem}.{test_stem}.corr")
                corrs.append(corr)
                ninja.build(
                    [outp, errp, infp],
                    "oiejq-bin",
                    [str(tmp / prog_stem), str(infile)],
                    variables=dict(
                        inp=str(infile),
                        outp=outp,
                        errp=errp,
                        infp=infp,
                        exe=str(tmp / prog_stem),
                    ),
                )
                ninja.build(
                    [corr],
                    "diff",
                    [outfile, outp],
                    ["custom-compare"] if customCompare else [],
                )
                timp = str(tmp / f"{prog_stem}.{test_stem}.tim")
                memp = str(tmp / f"{prog_stem}.{test_stem}.mem")
                timps.append(timp)
                memps.append(memp)
                ninja.build([memp], "extract-memory", [infp])
                ninja.build([timp], "extract-time", [infp])
            ninja.build([prog_stem + ".memsum"], "sum", memps)
            ninja.build([prog_stem + ".timesum"], "sum", timps)
            ninja.build([prog_stem + ".corrects"], "sum", corrs)
        ninja.build([str(tmp / "program_list")], "make-a-list", progs)


if __name__ == "__main__":
    main()
