<script>
  import { onMount } from 'svelte';
  export let program, test;
  let correct = null;
  let time = null;
  let memory = null;
  async function build() {
    fetch('/tmp/' + program + '.' + test + '.corr').then(r => r.text()).then(t => {
      correct = parseInt(t) > 0;
    });
    fetch('/tmp/' + program + '.' + test + '.mem').then(r => r.text()).then(t => {
      memory = parseInt(t);
    });
    fetch('/tmp/' + program + '.' + test + '.tim').then(r => r.text()).then(t => {
      time = parseInt(t);
    });
  }
  onMount(build);
</script>

<td>
  <p>
    {#if correct == null}
    correctness unknown
    {:else if correct}
    correct
    {:else}
    WRONG
    {/if}
  </p>
  <p>
    {#if time == null}
    time unknown
    {:else}
    {time}ms
    {/if}
  </p>
  <p>
    {#if memory == null}
    memory unknown
    {:else}
    {memory}KB
    {/if}
  </p>
  <p>
    <a href="/tmp/{program}.{test}.out">out</a>
    <a href="/tmp/{program}.{test}.err">err</a>
    <a href="/tmp/{program}.{test}.inf">inf</a>
  </p>
</td>

<style>
  td {
    text-align: right;
  }
</style>
