<script>
    import { onMount } from 'svelte';
    import { base } from '$app/paths';
    import { page } from '$app/stores';
    import { browser } from '$app/environment';
    import { writable } from "svelte/store";
    // ui stuff
    import { DataTable } from '@careswitch/svelte-data-table';
    import { Button, Col, Container, Input, Row, Table } from '@sveltestrap/sveltestrap';

	import { symbols } from './symbols.svelte.js';

	let { data } = $props();
    symbols.symbols = data.symbols;
    symbols.selected_version = data.selected_version;
    symbols.selected_versions_to_compare = data.selected_versions_to_compare;
    symbols.elfDataProvided = data.elfDataProvided;
    let files = $state();
    let versions = $derived(Object.keys(symbols.symbols));
    let selected_symbols = $state({});
    let selected_thread_stat = $state({});
    let selected_symbols_to_compare = $state({});
    let selected_thread_stat_to_compare = $state({});
    let symbols_to_show = $state({});
    let currentYear = $state(0);
    let function_table_data = $state([]);
    let variable_table_data = $state([]);
    let function_table = $derived(new DataTable({
        pageSize: 9999, // TODO
		data: function_table_data,
		columns: [
			{ id: 'name', key: 'display_name', name: 'Name' },
            { id: 'remark', key: 'remark', name: 'Remarks' },
			{ id: 'size', key: 'size', name: 'Code size' },
			{ id: 'd_size', key: 'd_size', name: 'Δ size' },
			{ id: 'stack_size', key: 'stack_size', name: 'Stack size'},
			{ id: 'd_stack', key: 'd_stack', name: 'Δ stack' },
		]
	}));
    let variable_table = $derived(new DataTable({
        pageSize: 9999, // TODO
		data: variable_table_data,
		columns: [
			{ id: 'name', key: 'display_name', name: 'Name' },
            { id: 'remark', key: 'remark', name: 'Remarks' },
			{ id: 'size', key: 'size', name: 'Static size' },
			{ id: 'd_size', key: 'd_size', name: 'Δ size' },
		]
	}));

    let symbolsToMap = (syms) => {
        let symMap = {};
        for (const sym of syms) {
            sym.remark = "";
            sym.newSymbols = false;
            sym.deletedSymbols = false;
            sym.d_size = null;
            sym.d_stack = null;
            symMap[sym.file+sym.display_name] = sym;
        }
        return symMap;
    }

    let symbolsToFunctionMap = (symMap) => {
        return Object.values(symMap).filter((e) => {return e["type"] === "function";})
    }

    let symbolsToVariableMap = (symMap) => {
        return Object.values(symMap).filter((e) => {return e["type"] === "variable";})
    }

    let symMapToSymNameSet = (symMap) => {
        return new Set(Object.keys(symMap));
    }

    const updateSelectedSymbols = () => {
        selected_symbols = symbolsToMap(symbols.symbols[symbols.selected_version]["symbols"]);
        selected_symbols_to_compare = symbolsToMap(symbols.symbols[symbols.selected_versions_to_compare]["symbols"]);
        selected_thread_stat = symbols.symbols[symbols.selected_version]["stack_reports"];
        selected_thread_stat_to_compare = symbols.symbols[symbols.selected_versions_to_compare]["stack_reports"];

        let symKey = symMapToSymNameSet(selected_symbols);
        let symKey_ref = symMapToSymNameSet(selected_symbols_to_compare);
        let newSymbols = Object.keys(Object.fromEntries(symKey.difference(symKey_ref).entries()));
        let deletedSymbols = Object.keys(Object.fromEntries(symKey_ref.difference(symKey).entries()));

        symbols_to_show = {};
        for (const symPath of deletedSymbols) {
            selected_symbols_to_compare[symPath].remark  += "Deleted!";
            if(selected_symbols_to_compare[symPath].size){
                selected_symbols_to_compare[symPath].d_size   = -selected_symbols_to_compare[symPath].size;
            }
            if(selected_symbols_to_compare[symPath].stack_size){
                selected_symbols_to_compare[symPath].d_stack  = -selected_symbols_to_compare[symPath].stack_size;
            }
            symbols_to_show[symPath] = selected_symbols_to_compare[symPath];
        }
        for (const symPath of Object.keys(selected_symbols)) {
            if(deletedSymbols.includes(symPath)){
                continue;
            }
            let shouldAdd = false;
            if(newSymbols.includes(symPath)){
                selected_symbols[symPath].remark += "Newly added!";
                shouldAdd = true;
            }
            else {
                // if not a new variable check if it has a change in code or stack size
                if (selected_symbols[symPath].size != selected_symbols_to_compare[symPath].size) {
                    selected_symbols[symPath].d_size = selected_symbols[symPath].size - selected_symbols_to_compare[symPath].size;
                    shouldAdd = true;
                }
                if (selected_symbols[symPath].stack_size != selected_symbols_to_compare[symPath].stack_size) {
                    selected_symbols[symPath].d_stack = selected_symbols[symPath].stack_size - selected_symbols_to_compare[symPath].stack_size;
                    shouldAdd = true;
                }
            }
            if(shouldAdd)
            {
                symbols_to_show[symPath] = selected_symbols[symPath];
            }
        }

        function_table_data = symbolsToFunctionMap(symbols_to_show);
        variable_table_data = symbolsToVariableMap(symbols_to_show);
        //alert(function_table_data.length+" !! "+variable_table_data.length)
        function_table = new DataTable({
            pageSize: function_table_data.length,
            data: function_table_data,
            columns: [
                { id: 'name', key: 'display_name', name: 'Name' },
                { id: 'remark', key: 'remark', name: 'Remarks' },
                { id: 'size', key: 'size', name: 'Code size' },
                { id: 'd_size', key: 'd_size', name: 'Δ size' },
                { id: 'stack_size', key: 'stack_size', name: 'Stack size'},
                { id: 'd_stack', key: 'd_stack', name: 'Δ stack' },
            ]
        });
        variable_table = new DataTable({
            pageSize: variable_table_data.length,
            data: variable_table_data,
                columns: [
                { id: 'name', key: 'name', name: 'Name' },
                { id: 'remark', key: 'remark', name: 'Remarks' },
                { id: 'size', key: 'size', name: 'Static size' },
                { id: 'd_size', key: 'd_size', name: 'Δ size' },
            ]
        });
    };


    const updateElfDataURL = () => {
            // TODO
    };

    const updateSelectedVersion = () => {
        localStorage.selected_version = symbols.selected_version;
        updateSelectedSymbols();
    };

    const updateSelectedVersionsToCompare = () => {
        localStorage.selected_versions_to_compare = symbols.selected_versions_to_compare;
        updateSelectedSymbols();
    };

	$effect(() => {
		if (files) {
			// Note that `files` is of type `FileList`, not an Array:
			// https://developer.mozilla.org/en-US/docs/Web/API/FileList
			console.log("files "+files);
            const file = files[0];

            // Validate file existence and type
            if (!file) {
                console.log("No file selected. Please choose a file.", "error");
                return;
            }

            if (!(file.type.endsWith("JSON") || file.type.endsWith("json"))) {
                console.log(file.type+"Unsupported file type. Please select a text file.", "error");
                return;
            }

            // Read the file
            const reader = new FileReader();
            reader.onload = () => {
                symbols.symbols = JSON.parse(reader.result);
            };
            reader.onerror = () => {
                showMessage("Error reading the file. Please try again.", "error");
            };
            reader.readAsText(file);
		}
	});

    onMount(async () => {
        if (browser) {
            currentYear = JSON.stringify(new Date().getFullYear());
            // load elf data
            if (Object.keys(symbols.symbols).length == 0) {
                console.log("No ELF data URL passed or stored, please upload it as a file then :)");
            } else {
                if(symbols.selected_version && symbols.selected_versions_to_compare)
                {
                    updateSelectedSymbols();
                } else {
                    console.log("ELF loaded, please select which version to show :)");
                }
            }
        }
    });
    // $inspect(selected_thread_stat);
    // $inspect(currentYear);
</script>

<style>
    /*
    @import 'static/css/style.css';
    */
    @import 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css';
</style>

<div class="container" id="content">

    <Row>
        <Col>
            Select a version of the .elf you want to see:
            <Input type="select"
                bind:value={symbols.selected_version}
                on:change={updateSelectedVersion}
            >
                {#each versions as version}
                    <option>{version}</option>
                {/each}
            </Input>
        </Col>
        <Col>
            Select a version of the .elf you want to compare against.
            <Input type="select"
                bind:value={symbols.selected_versions_to_compare}
                on:change={updateSelectedVersionsToCompare}
            >
                {#each versions as version}
                    <option>{version}</option>
                {/each}
            </Input>
        </Col>
      </Row>

      <hr>

    <Container fluid>
        {#if !symbols.elfDataProvided && files && !files[0]}
            <label for="elfinput">Upload a puncover .json file:</label>
            <input accept="*/json" bind:files id="elfinput" name="elfinput" type="file" />
        {:else if !symbols.selected_version}
            <h3>Select a version to browse elf symbols :)</h3>
        {:else}

            <h3>Summary</h3>

            <p>From {symbols.selected_version} to {symbols.selected_versions_to_compare} the change in...</p>
            <ul>
                <li>...flash/code size is {Object.values(symbols_to_show).filter((e) => {return e["d_size"] && e["type"] === "function";}).reduce((acc, b) => acc  + b["d_size"], 0)} bytes</li>
                <li>...static RAM size is {Object.values(symbols_to_show).filter((e) => {return e["d_size"] && e["type"] === "variable";}).reduce((acc, b) => acc  + b["d_size"], 0)} bytes</li>
                <li>...stack size is {Object.values(symbols_to_show).filter((e) => {return e["d_stack"];}).reduce((acc, b) => acc + b["d_stack"], 0)} bytes</li>
            </ul>

            {#key selected_thread_stat}
            <h3>Thread stats</h3>

            <p>From {symbols.selected_version} to {symbols.selected_versions_to_compare} the change in...</p>
            <ul>
                {#each Object.keys(selected_thread_stat) as thread_name (thread_name)}
                <li>
                    ...<b>{thread_name}'s</b> static stack usage is
                    {selected_thread_stat[thread_name].max_static_stack_size - selected_thread_stat_to_compare[thread_name].max_static_stack_size} bytes -
                    now at {selected_thread_stat[thread_name].max_static_stack_size} / {selected_thread_stat[thread_name].max_stack_size}
                </li>
                {/each}
            </ul>
            {/key}

            <h3>Function symbols for {symbols.selected_version}</h3>

            <Table>
                <thead>
                    <tr>
                        {#each function_table.columns as column (column.name)}
                            <th>
                                {column.name}
                                <button
                                    class="flex items-center"
                                    onclick={() => function_table.toggleSort(column.id)}
                                    disabled={!function_table.isSortable(column.id)}
                                >
                                    {#if function_table.isSortable(column.id)}
                                        <span class="ml-2">
                                            {#if function_table.getSortState(column.id) === 'asc'}
                                                ↑
                                                {:else if function_table.getSortState(column.id) === 'desc'}
                                                ↓
                                                {:else}
                                                ↕
                                                {/if}
                                            </span>
                                    {/if}
                                </button>
                            </th>
                        {/each}
                    </tr>
                </thead>
                <tbody>
                    {#each function_table.rows as row (row.file + row.name)}
                        <tr>
                            {#each function_table.columns as column (column.name)}
                                <td>{row[column.key]}</td>
                            {/each}
                        </tr>
                    {/each}
                </tbody>
            </Table>

            <h3>Variable symbols for {symbols.selected_version}</h3>

            <Table>
                <thead>
                    <tr>
                        {#each variable_table.columns as column (column.name)}
                        <th>
                            {column.name}
                            <button
                                class="flex items-center"
                                onclick={() => variable_table.toggleSort(column.id)}
                                disabled={!variable_table.isSortable(column.id)}
                            >
                                {#if variable_table.isSortable(column.id)}
                                    <span class="ml-2">
                                        {#if variable_table.getSortState(column.id) === 'asc'}
                                            ↑
                                            {:else if variable_table.getSortState(column.id) === 'desc'}
                                            ↓
                                            {:else}
                                            ↕
                                            {/if}
                                        </span>
                                {/if}
                            </button>
                        </th>
                        {/each}
                    </tr>
                </thead>
                <tbody>
                    {#each variable_table.rows as row (row.file + row.name)}
                        <tr>
                            {#each variable_table.columns as column (column.name)}
                                <td>{row[column.key]}</td>
                            {/each}
                        </tr>
                    {/each}
                </tbody>
            </Table>

            <!--
            {#each symbols[selected_version] as symbol}
            <li>{symbol["name"]} - {symbol["type"]}</li>
            {/each}

                functions-->
                <!--Name
                Remarks
                Stack
                Code
                Static
                    {% for symbol in (functions | sorted) %}
                    <tr>
                        <td><a href="{{ symbol | symbol_url }}" class="icon-function">{{ symbol.display_name |e }}</a></td>
                        <td>{{ symbol_remarks(symbol) }}</td>
                        <td class="col_size">
                            {{ symbol.stack_size | bytes }}
                            {% if symbol.stack_size and symbol.compared_stack_size  %}
                                {% if symbol.compared_stack_size > symbol.stack_size %}
                                    (+{{ symbol.compared_stack_size - symbol.stack_size }} bytes)
                                {% elif symbol.compared_stack_size < symbol.stack_size %}
                                    ({{ symbol.compared_stack_size - symbol.stack_size }} bytes)
                                {% endif %}
                            {% endif %}
                        </td>
                        <td class="col_size" style="{{ symbol.size | style_background_bar(group_code_size, color_bar_code) }}">
                        {{ symbol.size | bytes }}
                        {% if symbol.size and symbol.compared_size  %}
                            {% if symbol.compared_size > symbol.size %}
                                (+{{ symbol.compared_size - symbol.size }} bytes)
                            {% elif symbol.compared_size < symbol.size %}
                                ({{ symbol.compared_size - symbol.size }} bytes)
                            {% endif %}
                        {% endif %}
                        </td>
                        <td class="col_size"></td>
                    </tr>
                    {% endfor %}
                {% if functions | length > 1 and variables | length > 0 %}
                    <tr>
                        <th colspan="3">&sum; {{ functions | length }} functions</th>
                        <th class="col_size">{{ functions | symbol_code_size | bytes }}</th>
                        <th></th>
                    </tr>
                {% endif %}
-->
                <!--variables
                {% for var in variables | sorted %}
                    <tr>
                    <td colspan="4"><span class="icon-variable">{{ var.display_name |e }}</span></td>
                    <td class="col_size" style="{{ var | symbol_var_size | style_background_bar(group_var_size, color_bar_var) }}">
                        {{ var | symbol_var_size | bytes }}
                        {% if var.size and var.compared_size  %}
                        {% if var.compared_size > var.size %}
                            (+{{ var.compared_size - var.size }} bytes)
                        {% elif var.compared_size < var.size %}
                            ({{ var.compared_size - var.size }} bytes)
                        {% endif %}
                    {% endif %}
                    </td>
                </tr>
                {% endfor %}
            {% if variables | length > 1 and functions | length > 0 %}
                <tr>
                    <th colspan="4">&sum; {{ variables | length }} variables</th>
                    <th class="col_size">{{ variables | symbol_var_size | bytes }}</th>
                </tr>
            {% endif %}
                </tbody>

                <tfoot>
                    <tr>
                    <th colspan="3">&sum; over all
                        ({{ functions | length }} function{{ 's' if functions | length != 1}},
                         {{ variables | length }} variable{{ 's' if variables | length != 1}})

                    </th>
                    <th class="col_size">{{ group_code_size | bytes}}</th>
                    <th class="col_size">{{ group_var_size | bytes}}</th>
                    </tr>
                </tfoot>
            </table>
            -->
        {/if}
    </Container>

    <!-- {#if selected_version && selected_path === "/"}
    <Button color="warning" href="#/all">Show all symbols</Button>
    {/if} -->

    <hr>

    <div id="page-footer">
        brought to you with &#128150;
        by <a href="https://twitter.com/hbehrens">Heiko Behrens</a>, Paul Würtz
        <span class="secondary">– MIT license, copyright &copy; 2014-{{ currentYear }}</span>
    </div>
</div>



