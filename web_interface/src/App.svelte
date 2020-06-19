<script>
  import { onMount } from 'svelte';
  import Cell from './Cell.svelte';
  let programs = [];
  let tests = [];
  let extensions = {};
  async function build() {
    let [newTests, newPrograms] = await Promise.all([
      fetch('/tmp/test_list').then(r => r.text()).then(text => Promise.resolve(text.trim().split('\n'))),
      fetch('/tmp/program_list').then(r => r.text()).then(text => Promise.resolve(text.trim().split('\n'))),
    ]);
    programs = newPrograms.map(x => { x = x.split('/')[1]; let [stem, ext] = x.split('.'); extensions[stem] = ext; return stem; }).sort();
    tests = newTests.map(x => x.split('/')[1].split('.')[0]).sort();
  }

  onMount(build);
</script>

<main>
  <table border="1">
    <thead>
      <tr>
        <th />
        {#each tests as test}
        <th>
          {test}
          <a href="/tests/{test}.in">in</a>
          <a href="/tests/{test}.out">out</a>
        </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each programs as program}
      <tr>
        <th>
          {program}.{extensions[program]}
          <a href="/programs/{program}.{extensions[program]}">src</a>
        </th>
        {#each tests as test}
        <Cell {test} {program} />
        {/each}
      </tr>
      {/each}
    </tbody>
  </table>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 1000px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
