"""
Serviço de web scraping para consulta de processos no TJSP.
"""

import asyncio
from playwright.async_api import Browser


async def scrape_tjsp_process(browser: Browser, process_number: str) -> str:
    """
    Navega até o site do TJSP, busca por um número de processo e tira um screenshot.

    Args:
        browser: Instância do Playwright browser.
        process_number: O número do processo a ser buscado.

    Returns:
        O caminho do arquivo de screenshot salvo.
    """
    screenshot_path = f"./{process_number}_screenshot.png"
    
    page = await browser.new_page()
    try:
        # Navega para a página de consulta de primeiro grau
        await page.goto("https://esaj.tjsp.jus.br/cpopg/open.do", timeout=60000)

        # Preenche o número do processo
        parts = process_number.split('.')
        if len(parts) > 1:
            number_prefix = parts[0]
            number_suffix_parts = parts[1].split('-')
            if len(number_suffix_parts) > 1:
                number_suffix = number_suffix_parts[1]
            else:
                await page.locator("#numeroDigitoAnoUnificado").fill(process_number)
                
            await page.locator("#numeroDigitoAnoUnificado").fill(number_prefix)
            await page.locator("#foroNumeroUnificado").fill(number_suffix_parts[0])
        else:
            await page.locator("#numeroDigitoAnoUnificado").fill(process_number)

        # Clica no botão de busca e espera a navegação
        async with page.expect_navigation(timeout=30000):
            await page.locator("#botaoConsultarProcessos").click()

        # Tira um screenshot da página de resultados
        await page.screenshot(path=screenshot_path)

    except Exception as e:
        print(f"Erro durante o scraping: {e}")
        await page.screenshot(path="./error_screenshot.png")
        return f"Erro ao processar: {e}. Screenshot de erro salvo em error_screenshot.png"
    finally:
        await page.close()
            
    return screenshot_path