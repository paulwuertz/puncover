<script>
    let { children } = $props();
    import { base } from '$app/paths';
    import { Navbar, NavItem, NavLink, NavbarBrand } from '@sveltestrap/sveltestrap';
</script>

<nav>
  <Navbar color="light">
    <NavbarBrand href="{base}/">Puncover</NavbarBrand>

    <NavItem><NavLink href="{base}/symbols">Symbols</NavLink></NavItem>
    <NavItem><NavLink href="{base}/threads">Thread (TODO)</NavLink></NavItem>
    <NavItem><NavLink href="{base}/interrupts">Interrupts (TODO)</NavLink></NavItem>
    <NavItem><NavLink href="{base}/settings">Settings (TODO)</NavLink></NavItem>
    <NavItem><NavLink href="{base}/about">About</NavLink></NavItem>
  </Navbar>
  <!--- TODO add breadcrumbs-->
</nav>

{@render children()}
