<script>
    let { children } = $props();
    import { Navbar, NavItem, NavLink, NavbarBrand } from '@sveltestrap/sveltestrap';
</script>

<nav>
  <Navbar color="light">
    <NavbarBrand href="/">Puncover</NavbarBrand>

    <NavItem><NavLink href="/symbols">Symbols</NavLink></NavItem>
    <NavItem><NavLink href="/threads">Thread (TODO)</NavLink></NavItem>
    <NavItem><NavLink href="/interrupts">Interrupts (TODO)</NavLink></NavItem>
    <NavItem><NavLink href="/settings">Settings (TODO)</NavLink></NavItem>
    <NavItem><NavLink href="/about">About</NavLink></NavItem>
  </Navbar>
  <!--- TODO add breadcrumbs-->
</nav>

{@render children()}
