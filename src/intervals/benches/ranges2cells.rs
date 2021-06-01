
use criterion::{Criterion, black_box, criterion_group, criterion_main, BenchmarkId};

use intervals::moc::{RangeMOC, RangeMOCIntoIterator, RangeMOCIterator};
use intervals::mocranges::MocRanges;
use intervals::mocqty::{Hpx, MocQty};
use intervals::mocell::Cell;
use intervals::hpxranges::{HpxToUniqIter, HpxUniq2DepthIdxIter};
use intervals::ranges::Idx;
use std::cmp::Ordering;


fn create_ranges() -> RangeMOC<u64, Hpx<u64>> {
  RangeMOC {
    depth_max: 29,
    ranges: MocRanges::<u64, Hpx<u64>>::new_unchecked(vec![
      0..5,
      6..59,
      78..6953,
      12458..55587,
      55787..65587
    ])
  }
}

fn test_old_version<T: Idx>(ranges_moc: RangeMOC<T, Hpx<T>>) -> Vec<(i8, T)> {
  HpxUniq2DepthIdxIter::new(ranges_moc.ranges).collect()
}

fn test_new_version<T: Idx, Q: MocQty<T>>(ranges_moc: RangeMOC<T, Q>) -> Vec<Cell<T>> {
  ranges_moc.into_range_moc_iter().cells().collect()
}

fn test_new_version_ref<T: Idx, Q: MocQty<T>>(ranges_moc: &RangeMOC<T, Q>) -> Vec<Cell<T>> {
  let mut v: Vec<Cell<T>> = ranges_moc.into_range_moc_iter().cells().collect();
  v.sort_by(
    |a, b| match a.depth.cmp(&b.depth) {
      Ordering::Less => Ordering::Less,
      Ordering::Greater => Ordering::Greater,
      Ordering::Equal => a.idx.cmp(&b.idx)
    });
  v
}

fn bench_ranges2cells(c: &mut Criterion) {
  // https://bheisler.github.io/criterion.rs/book/user_guide/comparing_functions.html
  let mut group = c.benchmark_group("Ranges2Cells");
  let range_moc = create_ranges();
  /*group.bench_with_input(BenchmarkId::new("CDS HEALPix", '1'), &range_moc,
    |b, moc| b.iter(|| test_new_version(moc)));*/
  group.bench_function("CDS HEALPix",
    |b| b.iter(|| test_new_version(create_ranges())));
  group.bench_function("MOCPy",
    |b| b.iter(|| test_old_version(create_ranges())));
  group.bench_function("CDS HEALPix ref and sort",
    |b| b.iter(|| test_new_version_ref(&range_moc)));
}

criterion_group!(benches, bench_ranges2cells);
criterion_main!(benches);